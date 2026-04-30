"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2 } from "lucide-react";
import { useCivicRewards } from "./CivicRewardsContext";

const candidates = [
  { id: "c1", name: "Jane Doe", party: "Independent" },
  { id: "c2", name: "John Smith", party: "Nonpartisan" },
  { id: "c3", name: "Write-in", party: "" }
];

export default function MockBallot() {
  const [selected, setSelected] = useState<string | null>(null);
  const [isCast, setIsCast] = useState(false);
  const { awardBadge } = useCivicRewards();

  const handleCastBallot = () => {
    if (selected) {
      setIsCast(true);
      awardBadge("Civic Duty");
    }
  };

  return (
    <div className="py-20 bg-white">
      <div className="max-w-3xl mx-auto px-4">
        <div className="text-center mb-10">
          <h2 className="text-[2rem] font-bold text-[#212529] tracking-tight mb-4">
            Practice: Interactive Mock Ballot
          </h2>
          <p className="text-[1.125rem] text-[#495057]">
            Familiarize yourself with the voting interface in this secure, anonymous simulation.
          </p>
        </div>

        <div className="bg-[#F8F9FA] rounded-2xl p-8 border border-gray-200 shadow-sm relative overflow-hidden min-h-[400px] flex flex-col">
          
          <AnimatePresence mode="wait">
            {!isCast ? (
              <motion.div
                key="ballot"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                transition={{ duration: 0.4 }}
                className="flex-1 flex flex-col"
              >
                <div className="mb-6 border-b border-gray-300 pb-4">
                  <h3 className="text-xl font-bold text-[#212529]">City Council - District 1</h3>
                  <p className="text-sm font-medium text-[#E31937] mt-1">Vote for One</p>
                </div>

                <div className="flex flex-col gap-4 flex-1">
                  {candidates.map((candidate) => (
                    <label 
                      key={candidate.id}
                      className={`
                        flex items-center p-4 rounded-xl cursor-pointer transition-all border-2
                        ${selected === candidate.id 
                          ? 'border-[#005A9C] bg-[#005A9C]/5' 
                          : 'border-transparent bg-white hover:border-gray-300 hover:shadow-sm'}
                      `}
                    >
                      <div className="relative flex items-center justify-center w-8 h-8 mr-4">
                        <input 
                          type="radio" 
                          name="mock-council" 
                          value={candidate.id}
                          checked={selected === candidate.id}
                          onChange={() => setSelected(candidate.id)}
                          className="peer sr-only"
                        />
                        <div className="w-6 h-6 rounded-full border-2 border-gray-400 peer-checked:border-[#005A9C] transition-colors" />
                        <motion.div 
                          className="absolute w-3 h-3 rounded-full bg-[#005A9C]"
                          initial={false}
                          animate={{ scale: selected === candidate.id ? 1 : 0 }}
                          transition={{ type: "spring", stiffness: 300, damping: 20 }}
                        />
                      </div>
                      <div>
                        <div className="font-bold text-[#212529] text-lg">{candidate.name}</div>
                        {candidate.party && <div className="text-sm text-[#495057]">{candidate.party}</div>}
                      </div>
                    </label>
                  ))}
                </div>

                <div className="mt-8 pt-6 border-t border-gray-300 flex justify-end">
                  <button
                    onClick={handleCastBallot}
                    disabled={!selected}
                    className={`
                      px-8 py-3 rounded-lg font-bold text-white transition-all transform hover:scale-[1.02] min-h-[48px] min-w-[48px]
                      ${selected 
                        ? 'bg-[#005A9C] hover:bg-[#004a80] shadow-md' 
                        : 'bg-gray-400 cursor-not-allowed'}
                    `}
                  >
                    Cast Ballot
                  </button>
                </div>
              </motion.div>
            ) : (
              <motion.div
                key="success"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, type: "spring" }}
                className="flex-1 flex flex-col items-center justify-center text-center py-12"
              >
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                >
                  <CheckCircle2 className="w-24 h-24 text-[#005A9C] mb-6" strokeWidth={1.5} />
                </motion.div>
                
                <h3 className="text-[2rem] font-bold text-[#212529] mb-4">Ballot Secured</h3>
                <p className="text-[1.125rem] text-[#495057] max-w-md mx-auto mb-8">
                  Your mock ballot has been cast. In a real election, your vote is completely private and secure.
                </p>
                
                <button
                  onClick={() => { setSelected(null); setIsCast(false); }}
                  className="text-[#005A9C] font-semibold hover:underline"
                >
                  Reset Simulation
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
