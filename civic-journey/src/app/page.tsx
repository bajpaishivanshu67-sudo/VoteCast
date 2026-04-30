import Hero from "@/components/Hero";
import ScrollTimeline from "@/components/ScrollTimeline";
import MockBallot from "@/components/MockBallot";

export default function Home() {
  return (
    <div className="flex flex-col flex-1 w-full">
      <Hero />
      <ScrollTimeline />
      <MockBallot />
    </div>
  );
}
