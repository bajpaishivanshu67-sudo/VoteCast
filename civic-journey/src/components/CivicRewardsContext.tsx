"use client";

import React, { createContext, useContext, useState, ReactNode } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Award, ShieldCheck } from "lucide-react";

interface CivicContextType {
  badges: string[];
  awardBadge: (badge: string) => void;
}

const CivicContext = createContext<CivicContextType | undefined>(undefined);

export function CivicProvider({ children }: { children: ReactNode }) {
  const [badges, setBadges] = useState<string[]>([]);
  const [showNotification, setShowNotification] = useState<string | null>(null);

  const awardBadge = (badge: string) => {
    if (!badges.includes(badge)) {
      setBadges((prev) => [...prev, badge]);
      setShowNotification(badge);
      setTimeout(() => setShowNotification(null), 4000);
    }
  };

  return (
    <CivicContext.Provider value={{ badges, awardBadge }}>
      {children}
      
      {/* Floating Badge Notification */}
      <AnimatePresence>
        {showNotification && (
          <motion.div
            initial={{ opacity: 0, y: -50, scale: 0.8 }}
            animate={{ opacity: 1, y: 20, scale: 1 }}
            exit={{ opacity: 0, y: -50, scale: 0.8 }}
            className="fixed top-0 left-0 right-0 z-50 flex justify-center pointer-events-none"
          >
            <div className="bg-white px-6 py-4 rounded-full shadow-lg border border-[#005A9C]/20 flex items-center gap-3">
              <div className="bg-[#005A9C] text-white p-2 rounded-full">
                {showNotification === "Civic Duty" ? <ShieldCheck size={20} /> : <Award size={20} />}
              </div>
              <div>
                <p className="text-sm text-[#495057] font-medium m-0 leading-tight">Badge Unlocked!</p>
                <p className="text-lg font-bold text-[#005A9C] m-0 leading-tight">{showNotification}</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </CivicContext.Provider>
  );
}

export function useCivicRewards() {
  const context = useContext(CivicContext);
  if (context === undefined) {
    throw new Error("useCivicRewards must be used within a CivicProvider");
  }
  return context;
}

// Display Component for the Header
export function CivicBadgeTracker() {
  const { badges } = useCivicRewards();

  if (badges.length === 0) return null;

  return (
    <div className="flex items-center gap-2">
      {badges.map((badge, idx) => (
        <motion.div
          key={badge}
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ type: "spring", stiffness: 200, damping: 15 }}
          className="flex items-center gap-1.5 bg-[#F8F9FA] px-3 py-1.5 rounded-full border border-gray-200 shadow-sm"
          title={badge}
        >
          {badge === "Civic Duty" ? (
            <ShieldCheck size={16} className="text-[#005A9C]" />
          ) : (
            <Award size={16} className="text-[#005A9C]" />
          )}
          <span className="text-xs font-bold text-[#212529] hidden sm:inline-block">{badge}</span>
        </motion.div>
      ))}
    </div>
  );
}
