"use client";

import { useState, useRef, FormEvent, ChangeEvent, useEffect } from "react";
import Image from "next/image";
import { fetchAllDevelopers } from "@/lib/api";
import DeveloperCard from "@/components/DeveloperCard";
import { TextGenerateEffect } from "@/components/ui/text-generate-effect";

interface Message {
  text: string;
  isUser: boolean;
  metadata?: {
    node_type?: string;
    reason?: string;
    model?: string;
  };
  detectedDevelopers?: any[];
}

interface ApiResponse {
  status: string;
  query: string;
  answer: string;
  metadata: {
    node_type: string;
    reason: string;
    model?: string;
  };
  debug: {
    query: string;
    selected_node_type: string;
    index_name: string;
    selection_reason: string;
    available_node_types: Record<string, number>;
    retrieved_docs_count: number;
  };
}

// Model types for the dropdown
type ModelType = "ASI1-mini" | "Gemini 2.0";

export default function Home() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState<string>("");
  const [developers, setDevelopers] = useState<any[]>([]);
  const [selectedModel, setSelectedModel] = useState<ModelType>("ASI1-mini");
  const [showModelDropdown, setShowModelDropdown] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Load developers data
  useEffect(() => {
    const loadDevelopers = async () => {
      try {
        const data = await fetchAllDevelopers();
        setDevelopers(data);
      } catch (error) {
        console.error("Failed to load developers:", error);
      }
    };

    loadDevelopers();
    
    // Close dropdown when clicking outside
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowModelDropdown(false);
      }
    };
    
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Detect developer IDs in the text
  const detectDevelopers = (text: string) => {
    if (!developers || developers.length === 0) return [];

    const foundDevelopers: any[] = [];
    const lowerText = text.toLowerCase();
    
    developers.forEach(developer => {
      // Only match based on GitHub username (id)
      const username = developer.id?.toLowerCase();
      
      // Check if the GitHub username appears in the text
      if (username && lowerText.includes(username)) {
        foundDevelopers.push(developer);
      }
    });
    
    // Remove duplicates
    return Array.from(new Set(foundDevelopers));
  };

  const handleQueryChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
    setQuery(e.target.value);
    
    // Adjust textarea height based on content
    if (inputRef.current) {
      // Reset to default height first to get accurate scrollHeight measurement
      inputRef.current.style.height = "53px";
      
      // Only expand if content exceeds default height
      const scrollHeight = inputRef.current.scrollHeight;
      if (scrollHeight > 53) {
        const newHeight = Math.min(scrollHeight, 120); // Cap at 120px
        inputRef.current.style.height = `${newHeight}px`;
      }
    }
  };

  const toggleModelDropdown = () => {
    setShowModelDropdown(!showModelDropdown);
  };

  const selectModel = (model: ModelType) => {
    setSelectedModel(model);
    setShowModelDropdown(false);
  };

  const getEndpointForModel = () => {
    return selectedModel === "ASI1-mini" 
      ? "http://localhost:8000/chat"
      : "http://localhost:8000/geminichat";
  };

  const sendMessage = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!query.trim()) return;
    
    const userMessage = query.trim();
    setQuery("");
    
    // Reset textarea height properly
    if (inputRef.current) {
      inputRef.current.style.height = "53px"; // Reset to exact default height
    }
    
    // Add user message to the chat
    setMessages(prev => [...prev, { text: userMessage, isUser: true }]);
    setIsLoading(true);
    
    try {
      // First message becomes title, subsequent messages include history
      const payload = messages.length === 0 
        ? { query: userMessage }
        : { 
            query: `Past information: ${chatHistory}\n\nCurrent query: ${userMessage}`
          };
      
      // Use the appropriate endpoint based on selected model
      const endpoint = getEndpointForModel();
      
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
      
      if (!response.ok) {
        throw new Error("Failed to get response");
      }
      
      const data: ApiResponse = await response.json();
      
      // Add bot response to messages with metadata
      if (data.status === "success") {
        // Detect developer usernames/IDs in the response
        const detectedDevs = detectDevelopers(data.answer);
        
        // Add model information to metadata if not already there
        if (!data.metadata.model) {
          data.metadata.model = selectedModel;
        }
        
        setMessages(prev => [...prev, { 
          text: data.answer || "Sorry, I couldn't process that.", 
          isUser: false,
          metadata: data.metadata,
          detectedDevelopers: detectedDevs
        }]);
      } else {
        setMessages(prev => [...prev, { 
          text: "Sorry, I couldn't process that request.", 
          isUser: false,
          metadata: { model: selectedModel }
        }]);
      }
      
      // Update chat history
      const newHistory = messages.length === 0 
        ? userMessage 
        : `${chatHistory}\n\n${userMessage}`;
      
      setChatHistory(newHistory);
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage = "Sorry, an error occurred. Please try again.";
      setMessages(prev => [...prev, { 
        text: errorMessage,
        isUser: false,
        metadata: { model: selectedModel }
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Scroll to bottom when messages change
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="relative min-h-screen w-full">
      {/* Model selector dropdown (always visible) */}
      <div 
        ref={dropdownRef}
        className="absolute top-4 left-4 z-20"
      >
        <div 
          onClick={toggleModelDropdown}
          className="flex items-center gap-2 cursor-pointer p-2 rounded-md hover:bg-gray-100"
          style={{
            border: "1px solid #000D3D",
            borderRadius: "8px",
            padding: "8px 12px",
            background: "#FFFFFF"
          }}
        >
          <span style={{ color: "#000D3D", fontWeight: 500 }}>{selectedModel}</span>
          <Image 
            src="/icons/chevron-down.svg" 
            alt="Select model" 
            width={16} 
            height={16}
            style={{ transform: showModelDropdown ? 'rotate(180deg)' : 'rotate(0deg)' }}
          />
        </div>
        
        {showModelDropdown && (
          <div 
            className="absolute mt-1 bg-white shadow-lg rounded-md overflow-hidden"
            style={{ 
              border: "1px solid #E5E7EB",
              width: "100%",
              minWidth: "120px"
            }}
          >
            <div 
              className="px-4 py-2 cursor-pointer hover:bg-gray-100 flex items-center"
              onClick={() => selectModel("ASI1-mini")}
            >
              <span>ASI1-mini</span>
              {selectedModel === "ASI1-mini" && (
                <Image 
                  src="/icons/check.svg" 
                  alt="Selected" 
                  width={16} 
                  height={16}
                  className="ml-auto"
                />
              )}
            </div>
            <div 
              className="px-4 py-2 cursor-pointer hover:bg-gray-100 flex items-center"
              onClick={() => selectModel("Gemini 2.0")}
            >
              <span>Gemini 2.0</span>
              {selectedModel === "Gemini 2.0" && (
                <Image 
                  src="/icons/check.svg" 
                  alt="Selected" 
                  width={16} 
                  height={16}
                  className="ml-auto"
                />
              )}
            </div>
          </div>
        )}
      </div>
      
      {messages.length === 0 ? (
        // Initial search view
        <div className="flex flex-col items-center justify-center min-h-screen">
          <div className="flex flex-col items-center">
            <h1 
              style={{
                color: "#000D3D",
                fontFamily: "Inter",
                fontSize: "28px",
                fontWeight: 700,
                lineHeight: "normal"
              }}
            >
              Who are you looking for? 👀
            </h1>
            
            <div className="mt-6">
              <form onSubmit={sendMessage} className="relative">
                <textarea
                  ref={inputRef}
                  value={query}
                  onChange={handleQueryChange}
                  placeholder="Find who's behind the code"
                  style={{
                    width: "851px",
                    minHeight: "84px",
                    borderRadius: "10px",
                    border: "1px solid #000D3D",
                    padding: "20px",
                    paddingRight: "60px",
                    color: "#000D3D",
                    fontFamily: "Inter",
                    fontSize: "18px",
                    fontWeight: 400,
                    lineHeight: "normal",
                    resize: "none"
                  }}
                />
                <button 
                  type="submit"
                  className="absolute"
                  style={{
                    bottom: "16px",
                    right: "20px",
                  }}
                >
                  <Image 
                    src="/icons/send.svg" 
                    alt="Send" 
                    width={21} 
                    height={21} 
                  />
                </button>
              </form>
            </div>
          </div>
        </div>
      ) : (
        // Chat view after first message
        <div 
          ref={chatContainerRef}
          className="flex flex-col px-[328px] pt-[107px] pb-[120px] overflow-y-auto"
          style={{ height: "calc(100vh - 73px)" }}
        >
          <h1 
            style={{
              color: "#000D3D",
              fontFamily: "Inter",
              fontSize: "28px",
              fontWeight: 700,
              lineHeight: "normal"
            }}
          >
            {messages[0].text}
          </h1>
          
          <div className="mt-4 flex flex-col gap-4">
            {messages.slice(1).map((message, index) => (
              <div key={index} className="flex flex-col">
                <div 
                  className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                >
                  <div 
                    style={
                      message.isUser ? {
                        borderRadius: "100px",
                        border: "1px solid #000",
                        background: "#EFEFEF",
                        display: "inline-flex",
                        padding: "20px 32px",
                        justifyContent: "center",
                        alignItems: "center",
                        gap: "10px",
                        maxWidth: "80%"
                      } : {
                        padding: "20px 0",
                        maxWidth: "80%",
                        width: "100%" // Ensure full width for the TextGenerateEffect
                      }
                    }
                  >
                    {message.isUser ? (
                      message.text
                    ) : (
                      <TextGenerateEffect 
                        words={message.text} 
                        duration={1.5}
                        filter={false}
                        className="text-base font-normal"
                      />
                    )}
                    {message.metadata && (
                      <div className="mt-2 text-sm opacity-70">
                        {message.metadata.model && (
                          <div>Model: {message.metadata.model}</div>
                        )}
                        <div>Source: {message.metadata.node_type}</div>
                        {message.metadata.reason && (
                          <div>Reason: {message.metadata.reason}</div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Display developer cards if IDs are detected in the bot response */}
                {!message.isUser && message.detectedDevelopers && message.detectedDevelopers.length > 0 && (
                  <div className="mt-8">
                    {message.detectedDevelopers.map((developer, devIndex) => (
                      <div key={devIndex} className="mb-8">
                        <DeveloperCard developer={developer} />
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start mt-4">
                <div 
                  className="animate-pulse"
                  style={{
                    borderRadius: "100px",
                    background: "#EFEFEF",
                    width: "300px",
                    height: "10px",
                    flexShrink: 0
                  }}
                >
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Input bar fixed at bottom for chat mode */}
      {messages.length > 0 && (
        <div 
          className="fixed bottom-0 left-0 right-0 bg-white z-10"
          style={{ 
            paddingLeft: "328px", 
            paddingRight: "328px", 
            paddingTop: "10px", 
            paddingBottom: "10px",
          }}
        >
          <form onSubmit={sendMessage} className="relative">
            <textarea
              ref={inputRef}
              value={query}
              onChange={handleQueryChange}
              placeholder="Ask a follow up question"
              style={{
                width: "100%",
                height: "53px", // Explicitly set default height
                minHeight: "53px", // Set min-height to match
                maxHeight: "120px", // Limit maximum expansion
                borderRadius: "10px",
                border: "1px solid #000",
                padding: "15px 50px 15px 20px",
                fontSize: "18px",
                fontFamily: "Inter",
                fontWeight: 400,
                lineHeight: "normal",
                resize: "none",
                opacity: query ? 1 : 0.5,
                verticalAlign: "middle",
                overflow: "hidden"
              }}
            />
            <button 
              type="submit"
              className="absolute"
              style={{
                top: "50%",
                right: "24px",
                transform: "translateY(-50%)"
              }}
            >
              <Image 
                src="/icons/send.svg" 
                alt="Send" 
                width={21} 
                height={21} 
              />
            </button>
          </form>
        </div>
      )}
    </div>
  );
}