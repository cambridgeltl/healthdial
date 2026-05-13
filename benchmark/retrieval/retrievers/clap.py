import torch
import torchaudio
from laion_clap import CLAP_Module
from torch.nn.functional import cosine_similarity
from tqdm import tqdm

MAX_AUDIO_SECONDS = 60 # maximum 60 seconds
TARGET_SR = 48000  # 16kHz
MAX_AUDIO_SAMPLES = MAX_AUDIO_SECONDS * TARGET_SR  # e.g., 5*16000=80000 samples



class CLAPRetriever:
    def __init__(self, corpus_texts, language, device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = CLAP_Module(enable_fusion=False)
        self.model.load_ckpt()  # Load pretrained weights
        self.model.to(self.device)
        self.corpus = corpus_texts
        self.index()

    def index(self):
        print("Encoding text corpus...")
        with torch.no_grad():
            self.text_embs = self.model.get_text_embedding(self.corpus, use_tensor=True).to(self.device)  # (N, D)

    def retrieve(self, audio_path, top_k=5):
        waveform, sr = torchaudio.load(audio_path)
        try:
            waveform = waveform.mean(dim=0).unsqueeze(0)  # Mono
            if sr != TARGET_SR:
                waveform = torchaudio.functional.resample(waveform, sr, TARGET_SR)
            # if waveform.size(1) > MAX_AUDIO_SAMPLES:
            #     waveform = waveform[:, :MAX_AUDIO_SAMPLES]
            waveform = waveform.to(self.device)
        except Exception as e:
            print(f"Error processing audio file: {e}")
            return []

        with torch.no_grad():
            audio_emb = self.model.get_audio_embedding_from_data(x=waveform, use_tensor=True)  # (1, D)

        sims = cosine_similarity(audio_emb, self.text_embs).squeeze(0)
        top_indices = torch.topk(sims, top_k).indices.tolist()
        return [(self.corpus[i], sims[i].item()) for i in top_indices]