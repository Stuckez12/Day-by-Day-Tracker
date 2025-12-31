interface MessageProps {
    text: string
}

function Message({ text }: MessageProps) {
    return <h1>{text}</h1>;
}

export default Message;