import React, { useState, useEffect, useRef } from 'react';
import { Container, Row, Col, Card, Form, Button, InputGroup } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPaperPlane, faRobot, faLightbulb, faQuestionCircle, faInfoCircle } from '@fortawesome/free-solid-svg-icons';
import axios from 'axios';
import './AIAssistant.css';

const AIAssistant = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([
    'كيف يمكنني إضافة منشأة جديدة؟',
    'كيف يمكنني إنشاء حملة تسويقية؟',
    'كيف يمكنني تصدير البيانات؟',
    'كيف يمكنني ربط النظام مع تطبيقات الأتمتة؟'
  ]);
  const messagesEndRef = useRef(null);

  // إضافة رسالة ترحيبية عند تحميل المكون
  useEffect(() => {
    setMessages([
      {
        id: 1,
        sender: 'ai',
        content: 'مرحباً بك في المساعد الذكي لنظام E-deal! كيف يمكنني مساعدتك اليوم؟',
        timestamp: new Date()
      }
    ]);
  }, []);

  // التمرير إلى آخر الرسائل عند إضافة رسالة جديدة
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // إرسال رسالة إلى المساعد الذكي
  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      sender: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages([...messages, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post('/api/ai-assistant/chat', {
        message: input
      });

      const aiMessage = {
        id: messages.length + 2,
        sender: 'ai',
        content: response.data.response,
        timestamp: new Date()
      };

      setMessages(prevMessages => [...prevMessages, aiMessage]);
      setLoading(false);
    } catch (error) {
      console.error('Error sending message to AI assistant:', error);
      
      const errorMessage = {
        id: messages.length + 2,
        sender: 'ai',
        content: 'عذراً، حدث خطأ أثناء معالجة طلبك. يرجى المحاولة مرة أخرى.',
        timestamp: new Date(),
        isError: true
      };

      setMessages(prevMessages => [...prevMessages, errorMessage]);
      setLoading(false);
    }
  };

  // استخدام اقتراح
  const useSuggestion = (suggestion) => {
    setInput(suggestion);
  };

  // تنسيق التاريخ والوقت
  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('ar-SA', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // معالجة الضغط على Enter
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  return (
    <Container fluid className="ai-assistant-container">
      <h1 className="page-title">المساعد الذكي</h1>
      
      <Row>
        <Col lg={8}>
          <Card className="chat-card">
            <Card.Header>
              <div className="d-flex align-items-center">
                <div className="ai-avatar">
                  <FontAwesomeIcon icon={faRobot} />
                </div>
                <div className="ms-3">
                  <h5 className="mb-0">مساعد E-deal الذكي</h5>
                  <small className="text-muted">متصل</small>
                </div>
              </div>
            </Card.Header>
            <Card.Body className="chat-body">
              <div className="messages-container">
                {messages.map(message => (
                  <div 
                    key={message.id} 
                    className={`message ${message.sender === 'user' ? 'user-message' : 'ai-message'} ${message.isError ? 'error-message' : ''}`}
                  >
                    <div className="message-content">
                      {message.content}
                    </div>
                    <div className="message-timestamp">
                      {formatTimestamp(message.timestamp)}
                    </div>
                  </div>
                ))}
                {loading && (
                  <div className="message ai-message">
                    <div className="message-content">
                      <div className="typing-indicator">
                        <span></span>
                        <span></span>
                        <span></span>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </Card.Body>
            <Card.Footer>
              <InputGroup>
                <Form.Control
                  placeholder="اكتب رسالتك هنا..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={loading}
                />
                <Button 
                  variant="primary" 
                  onClick={sendMessage}
                  disabled={!input.trim() || loading}
                >
                  <FontAwesomeIcon icon={faPaperPlane} />
                </Button>
              </InputGroup>
            </Card.Footer>
          </Card>
        </Col>
        
        <Col lg={4}>
          <Card className="suggestions-card mb-4">
            <Card.Header>
              <FontAwesomeIcon icon={faLightbulb} className="me-2" />
              اقتراحات
            </Card.Header>
            <Card.Body>
              <div className="suggestions-list">
                {suggestions.map((suggestion, index) => (
                  <div 
                    key={index} 
                    className="suggestion-item"
                    onClick={() => useSuggestion(suggestion)}
                  >
                    {suggestion}
                  </div>
                ))}
              </div>
            </Card.Body>
          </Card>
          
          <Card className="help-card">
            <Card.Header>
              <FontAwesomeIcon icon={faQuestionCircle} className="me-2" />
              مساعدة
            </Card.Header>
            <Card.Body>
              <h5>ما الذي يمكن للمساعد الذكي فعله؟</h5>
              <ul className="help-list">
                <li>
                  <FontAwesomeIcon icon={faInfoCircle} className="me-2" />
                  الإجابة على الأسئلة حول استخدام النظام
                </li>
                <li>
                  <FontAwesomeIcon icon={faInfoCircle} className="me-2" />
                  تقديم إرشادات خطوة بخطوة للمهام المختلفة
                </li>
                <li>
                  <FontAwesomeIcon icon={faInfoCircle} className="me-2" />
                  شرح ميزات النظام وكيفية استخدامها
                </li>
                <li>
                  <FontAwesomeIcon icon={faInfoCircle} className="me-2" />
                  تقديم اقتراحات لتحسين استخدام النظام
                </li>
              </ul>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default AIAssistant;
