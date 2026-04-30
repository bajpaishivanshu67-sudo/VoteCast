"use client";

import { motion } from "framer-motion";

export default function Hero() {
  return (
    <div className="relative overflow-hidden bg-[#F8F9FA] min-h-[60vh] flex items-center justify-center">
      <div className="absolute inset-0 pointer-events-none opacity-30">
        <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern
              id="grid"
              width="40"
              height="40"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 40 0 L 0 0 0 40"
                fill="none"
                stroke="#005A9C"
                strokeWidth="0.5"
                opacity="0.2"
              />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
          
          <motion.g
            initial={{ y: -50, opacity: 0 }}
            animate={{ y: [0, -20, 0], opacity: 0.6 }}
            transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
          >
            <rect x="15%" y="20%" width="60" height="60" rx="8" fill="none" stroke="#005A9C" strokeWidth="2" />
            <line x1="25%" y1="25%" x2="45%" y2="25%" stroke="#005A9C" strokeWidth="2" />
          </motion.g>

          <motion.g
            initial={{ y: 50, opacity: 0 }}
            animate={{ y: [0, 30, 0], opacity: 0.4 }}
            transition={{ duration: 8, repeat: Infinity, ease: "easeInOut", delay: 1 }}
          >
            <circle cx="80%" cy="60%" r="40" fill="none" stroke="#E31937" strokeWidth="2" />
          </motion.g>

          <motion.g
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: [1, 1.1, 1], opacity: 0.5 }}
            transition={{ duration: 5, repeat: Infinity, ease: "easeInOut", delay: 2 }}
          >
             <path d="M 85% 25% L 90% 35% L 95% 20%" fill="none" stroke="#005A9C" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
          </motion.g>

        </svg>
      </div>

      <div className="relative z-10 text-center px-4 max-w-4xl mx-auto">
        <motion.h1 
          className="text-[2.5rem] font-bold tracking-tight text-[#212529] mb-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        >
          Your Voice, Demystified.
        </motion.h1>
        <motion.p 
          className="text-[1.125rem] font-normal leading-[1.6] text-[#495057] max-w-2xl mx-auto"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut", delay: 0.2 }}
        >
          Empowering you to navigate the electoral process with confidence and clarity.
        </motion.p>
      </div>
    </div>
  );
}
