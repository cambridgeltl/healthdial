export type TaskType = {
    task_id: string;
    language: string;
    utterance: UtteranceType[];
};

export type UtteranceType = {
    role: string;
    generated_text: string;
    instruction: string;
    snippet: KnowledgeSnippetType[];
    out_of_knowledge: boolean;
};


export type KnowledgeSnippetType = {
    url: string;
    language: string;
    data: KnowledgeSnippetDataType;
    parallel_data: boolean;
    parallel_identifier: string;
    unique_identifier: string;
};

export type KnowledgeSnippetDataType = {
    type: string;
    topic: string;
    title: string;
    content: string;
};


// export type SubmissionItemType = {
//     transcription: string;
// };

export type SubmissionValueType = string | Blob | null;


export type SubmissionDicType = {
    [key: string]: SubmissionValueType;
};

export type SubmissionItem = {
    blob_data: Blob | null; // The blob data or null if not provided
    transcription: string;  // The transcription string
    asr: string;            // The ASR (Automatic Speech Recognition) result string
};

