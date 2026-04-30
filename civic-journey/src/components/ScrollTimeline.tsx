"use client";

import { motion, useScroll, useSpring } from "framer-motion";
import { useRef } from "react";
import ProcessCard from "./ProcessCard";

const timelineData = [
  {
    title: "Voter Registration",
    summary: "Ensure you are eligible and registered to vote in your state before the deadline.",
    details: "Registration deadlines vary significantly by state. Some allow Same-Day Registration, while others require registration up to 30 days before Election Day. You will typically need a valid State ID or Social Security Number. You can register online, by mail, or in-person at designated government offices."
  },
  {
    title: "Researching Candidates",
    summary: "Learn about the candidates and ballot measures to make informed decisions.",
    details: "Review sample ballots provided by your local election office. Research candidate platforms, voting records, and endorsements. Non-partisan organizations often provide comprehensive voter guides detailing candidate positions on key issues."
  },
  {
    title: "Finding the Polling Place",
    summary: "Locate your designated voting location and verify its hours of operation.",
    details: "Your polling place is determined by your residential address and may change between elections. Always verify your location through your state's election portal before Election Day. Early voting locations often differ from Election Day polling places."
  },
  {
    title: "Casting the Vote",
    summary: "Complete your ballot securely, either in-person or via a mail-in absentee ballot.",
    details: "When voting in person, be prepared to show acceptable ID if your state requires it. If voting by mail, carefully follow all instructions regarding signatures, witness requirements, and return deadlines. Ensure your ballot is postmarked or returned to a secure drop box on time."
  }
];

export default function ScrollTimeline() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start center", "end center"]
  });

  const scaleY = useSpring(scrollYProgress, {
    stiffness: 100,
    damping: 30,
    restDelta: 0.001
  });

  return (
    <div className="py-20 bg-[#F8F9FA] relative" ref={containerRef}>
      <div className="max-w-4xl mx-auto px-4 relative">
        
        {/* The Animated Vertical Line */}
        <div className="absolute left-[1.5rem] sm:left-[2rem] top-0 bottom-0 w-1 bg-gray-200 rounded-full hidden sm:block overflow-hidden">
          <motion.div 
            className="w-full bg-[#005A9C] origin-top"
            style={{ scaleY, height: '100%' }}
          />
        </div>

        <div className="flex flex-col gap-8 items-start sm:pl-12">
          {timelineData.map((step, index) => (
            <ProcessCard 
              key={index}
              stepNumber={index + 1}
              title={step.title}
              summary={step.summary}
              details={step.details}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
