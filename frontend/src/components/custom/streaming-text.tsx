import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Markdown } from './markdown';

interface StreamingTextProps {
  text: string;
  delay?: number;
  speed?: number;
}

export function StreamingText({ text, delay = 0, speed = 30 }: StreamingTextProps) {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isStarted, setIsStarted] = useState(false);

  useEffect(() => {
    // Start streaming after delay
    if (!isStarted) {
      const startTimer = setTimeout(() => {
        setIsStarted(true);
      }, delay);
      return () => clearTimeout(startTimer);
    }

    // Stream characters
    if (isStarted && currentIndex < text.length) {
      const timer = setTimeout(() => {
        setDisplayedText(prev => prev + text[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, speed);

      return () => clearTimeout(timer);
    }
  }, [currentIndex, text, delay, speed, isStarted]);

  if (!isStarted) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <Markdown>{displayedText}</Markdown>
      {currentIndex < text.length && (
        <motion.span
          animate={{ opacity: [1, 0] }}
          transition={{ duration: 0.8, repeat: Infinity }}
          className="inline-block w-0.5 h-4 bg-current ml-1"
        />
      )}
    </motion.div>
  );
}
