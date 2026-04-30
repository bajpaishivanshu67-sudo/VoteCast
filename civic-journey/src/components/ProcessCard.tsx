"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";

interface ProcessCardProps {
  title: string;
  summary: string;
  details: string;
  stepNumber: number;
}

export default function ProcessCard({ title, summary, details, stepNumber }: ProcessCardProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <motion.div
      className="relative bg-white rounded-xl p-6 mb-8 w-full max-w-2xl ml-8 sm:ml-12 shadow-[0_4px_20px_-4px_rgba(0,0,0,0.05)] border border-gray-100"
      initial={{ opacity: 0, x: -50 }}
      whileInView={{ opacity: 1, x: 0 }}
      viewport={{ once: true, margin: "-100px" }}
      transition={{ duration: 0.6, ease: "easeOut" }}
    >
      {/* Connector Dot */}
      <div className="absolute left-[-2rem] sm:left-[-3rem] top-8 w-4 h-4 rounded-full bg-[#005A9C] ring-4 ring-white z-10 hidden sm:block" />

      <div className="flex items-center gap-4 mb-3">
        <span className="flex items-center justify-center w-8 h-8 rounded-full bg-[#F8F9FA] text-[#005A9C] font-bold text-sm">
          {stepNumber}
        </span>
        <h2 className="text-[1.5rem] font-bold text-[#212529] tracking-tight m-0">
          {title}
        </h2>
      </div>

      <p className="text-[1.125rem] font-normal leading-[1.6] text-[#495057] mb-4">
        {summary}
      </p>

      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 text-[#005A9C] font-semibold text-sm hover:underline focus:outline-none focus:ring-2 focus:ring-[#005A9C] focus:ring-offset-2 rounded-md px-2 py-1 -ml-2 transition-all min-h-[48px] min-w-[48px]"
        aria-expanded={isOpen}
      >
        {isOpen ? "Hide Details" : "View Full Details"}
        <motion.div
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.3 }}
        >
          <ChevronDown size={16} />
        </motion.div>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <div className="mt-4 p-4 bg-[#F8F9FA] rounded-lg text-[0.875rem] font-medium text-[#495057] leading-relaxed border-l-4 border-[#005A9C]">
              {details}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
