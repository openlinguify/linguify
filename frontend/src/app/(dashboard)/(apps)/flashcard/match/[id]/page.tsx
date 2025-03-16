"use client";

import { useParams } from "next/navigation";
import MatchGame from "../../_components/match-mode/match-game";

export default function MatchPage() {
  const { id } = useParams<{ id: string }>();
  
  return <MatchGame />;
}