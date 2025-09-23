export interface MessagePart {
    type: 'thought' | 'text' | 'function';
    content: string;
    author?: string;
    data?: unknown;
}

export interface message{
    content: string;
    role: string;
    id: string;
    parts?: MessagePart[];
}