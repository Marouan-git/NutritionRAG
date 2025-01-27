const Message = ({ message, isUser }) => {
    return (
      <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
        <div
          className={`rounded-lg px-4 py-2 max-w-[70%] ${
            isUser 
              ? 'bg-green-500 text-white' 
              : 'bg-gray-100 text-gray-800'
          }`}
        >
          {message.content}
          {message.pending && (
            <span className="ml-2 inline-block h-2 w-2 animate-pulse rounded-full bg-blue-500"></span>
          )}
        </div>
      </div>
    );
  };

  export default Message;