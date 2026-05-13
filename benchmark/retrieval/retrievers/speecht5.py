import torch
import torchaudio
import numpy as np
from torch.nn.functional import cosine_similarity
from transformers import SpeechT5Processor, SpeechT5Model
from transformers.models.speecht5.modeling_speecht5 import SpeechT5EncoderWithTextPrenet, SpeechT5EncoderWithSpeechPrenet
from .base import BaseRetriever
from tqdm import tqdm

MAX_AUDIO_SECONDS = 60  # maximum 60 seconds
TARGET_SR = 16000  # 16kHz

MAX_AUDIO_SAMPLES = MAX_AUDIO_SECONDS * TARGET_SR  # e.g., 5*16000=80000 samples

class SpeechT5Retriever(BaseRetriever):
    def __init__(self, corpus, language="eng"):
        super().__init__(corpus, language)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_asr")
        
        # Load the config
        self.config = SpeechT5Model.from_pretrained("microsoft/speecht5_asr").config

        # Initialize encoder with TEXT PRENET
        self.text_encoder = SpeechT5EncoderWithTextPrenet(self.config)

        # Initialize encoder with SPEECH PRENET
        self.speech_encoder = SpeechT5EncoderWithSpeechPrenet(self.config)

        # Load the full model
        self.model_text = SpeechT5Model(self.config, encoder=self.text_encoder).to(self.device)
        self.model_audio = SpeechT5Model(self.config, encoder=self.speech_encoder).to(self.device)

        self.max_seq_len = 450  # SpeechT5 max input length


    def index(self):
        self.text_embeddings = []
        for text in tqdm(self.corpus, desc="Indexing corpus"):
            inputs = self.processor(
                text=[text], 
                return_tensors="pt", 
                padding=False,  # Don't pad first
                truncation=False  # Don't truncate first
            )
            input_ids = inputs['input_ids'].to(self.device)
            attention_mask = inputs['attention_mask'].to(self.device)

            # Left-truncate manually
            if input_ids.size(1) > self.max_seq_len:
                input_ids = input_ids[:, -self.max_seq_len:]  # keep the last max_seq_len tokens
                attention_mask = attention_mask[:, -self.max_seq_len:]

            # Now pad to max_seq_len if needed
            pad_len = self.max_seq_len - input_ids.size(1)
            if pad_len > 0:
                pad = torch.full((1, pad_len), self.processor.tokenizer.pad_token_id, device=self.device)
                input_ids = torch.cat([pad, input_ids], dim=1)
                attention_mask = torch.cat([torch.zeros((1, pad_len), device=self.device), attention_mask], dim=1)

            with torch.no_grad():
                outputs = self.text_encoder(
                    input_values=input_ids, 
                    attention_mask=attention_mask,
                )
                text_emb = outputs.last_hidden_state.mean(dim=1)

            self.text_embeddings.append(text_emb.squeeze(0).cpu())

        self.text_embeddings = torch.stack(self.text_embeddings)

        
    def retrieve(self, audio_path, top_k=5):
        torch.cuda.empty_cache()
        waveform, sr = torchaudio.load(audio_path)
        if sr != TARGET_SR:
            try:
                waveform = torchaudio.functional.resample(waveform, sr, TARGET_SR)
            except Exception as e:
                print(f"Error resampling audio: {e}")
                return []
        # Truncate waveform if too long
        if waveform.size(1) > MAX_AUDIO_SAMPLES:
            waveform = waveform[:, :MAX_AUDIO_SAMPLES]
        inputs = self.processor(audio=waveform.squeeze(0), sampling_rate=16000, return_tensors="pt")
        input_values = inputs["input_values"].to(self.device)
        attention_mask = inputs.get("attention_mask", None)
        if attention_mask is not None:
            attention_mask = attention_mask.to(self.device)

        with torch.no_grad():
            # try to encode, if it fails, skip this audio
            try:
                encoder_out = self.model_audio.encoder(input_values=input_values, attention_mask=attention_mask)
            except Exception as e:
                print(f"Error encoding audio: {e}")
                return []
            audio_emb = encoder_out.last_hidden_state.mean(dim=1).cpu()  # (batch_size, hidden_dim)

        similarities = cosine_similarity(audio_emb, self.text_embeddings).squeeze(0)
        top_indices = torch.topk(similarities, top_k).indices.cpu().tolist()
        return [(self.corpus[i], similarities[i].item()) for i in top_indices]