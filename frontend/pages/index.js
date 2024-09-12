'use client';
import React, { useEffect, useRef, useState } from "react";
import TelegramIcon from "@mui/icons-material/Telegram";
import { Input, Typography, CircularProgress, Snackbar, IconButton } from "@mui/material";
import FavoriteIcon from "@mui/icons-material/Favorite";
import LinkedInIcon from "@mui/icons-material/LinkedIn";
//import alanBtn from "@alan-ai/alan-sdk-web";
import axios from "axios";
import { useLocation } from "react-router-dom";
import CloseIcon from '@mui/icons-material/Close';
import { useSelector } from "react-redux";

const ChatGPTUI = () => {
  const currentYear = new Date().getFullYear();
  const authId = useSelector((state) => state.authId);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const scroll = useRef();
  const location = useLocation();
  const alanBtnRef = useRef(null);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarText, setSnackbarText] = useState('');

  useEffect(() => {
    if (location.pathname === '/uoncom-gpt' && authId === "1") {
      alanBtnRef.current = alanBtn({
        key: `${process.env.REACT_APP_ALAN_KEY}`,
      });
    }
    return () => {
      if (alanBtnRef.current) {
        alanBtnRef.current.deactivate();
        alanBtnRef.current = null;
      }
    };
  }, [location.pathname, authId]);

  useEffect(() => {
    if (scroll.current) {
      scroll.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleMessageSend = async () => {
    if (!inputMessage.trim()) return;
    setInputMessage("");
    setMessages((prevMessages) => [...prevMessages, { text: inputMessage, sender: "user" }]);

    if (!navigator.onLine) {
      setSnackbarText('Please check your internet connection and try again.');
      setSnackbarOpen(true);
      return;
    }

    setMessages(prevMessages => [...prevMessages, { loader: true, sender: "bot" }]);

    try {
      const response = await axios.post("https://uoncom-ai-node-js.onrender.com/message", { message: inputMessage });
      animateBotResponse(response.data.response, true);
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { loader: false, text: "There was an error sending your message. Please try again.", sender: "bot" }
      ]);
    }
  };

  const animateBotResponse = (response, replaceThinking = false) => {
    const characters = response.split("");
    let animatedResponse = "";
    let animationStarted = false;

    characters.forEach((char, index) => {
      setTimeout(() => {
        animatedResponse += char;
        setMessages((prevMessages) => {
          let newMessages = [...prevMessages];
          if (!animationStarted && replaceThinking) {
            newMessages[newMessages.length - 1] = { text: animatedResponse, sender: "bot" };
            animationStarted = true;
          } else {
            newMessages[newMessages.length - 1].text = animatedResponse;
          }
          if (index === characters.length - 1) {
            newMessages[newMessages.length - 1].isComplete = true;
          }
          return newMessages;
        });
      }, 10 * index);
    });
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  const startRecording = () => {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onresult = (event) => {
      const speechText = event.results[0][0].transcript;
      setInputMessage(speechText);
      handleMessageSend();  // Automatically send the message
    };

    recognition.start();
  };

  return (
    <div className="flex flex-col h-screen">
      <div className="fixed top-19 left-0 flex flex-col md:flex-row h-screen w-full z-10">
        <div className="hidden md:block bg-transparent w-1/3 md:w-1/4 p-4 border-r-2 border-blue-500">
          <center>
            <img src="/media/images/UONCOM-3.png" alt="UoNCOM" style={{ height: 350, width: 350, marginTop: -60, objectFit: 'contain' }} />
          </center>
          <Typography variant="small" className="mb-4 text-center font-normal text-blue-gray-200 md:mb-0" style={{ marginLeft: 10 }}>
            © {currentYear} Created with <FavoriteIcon className="text-red-700 font-medium" /> by <a className="font-bold text-blue-500" href="https://jessy-bandya.web.app/">Jessy Bandya</a> for a better Future
          </Typography>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', padding: '10px', border: '1px solid #ddd', borderRadius: '5px', marginTop: '20px' }}>
          <Input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Type a message"
            style={{ flex: 1, padding: '10px', fontSize: '16px', borderRadius: '5px', border: '1px solid #ddd', marginRight: '10px' }}
          />
          <button onClick={startRecording} style={{ padding: '10px', fontSize: '16px', cursor: 'pointer', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '5px', marginRight: '10px' }}>
            🎤
          </button>
          <TelegramIcon onClick={handleMessageSend} style={{ cursor: 'pointer', color: '#28a745', fontSize: '32px' }} />
        </div>
      </div>
      <Snackbar
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={handleSnackbarClose}
        message={snackbarText}
        action={
          <IconButton size="small" aria-label="close" color="inherit" onClick={handleSnackbarClose}>
            <CloseIcon fontSize="small" />
          </IconButton>
        }
      />
    </div>
  );
};

export default ChatGPTUI;
