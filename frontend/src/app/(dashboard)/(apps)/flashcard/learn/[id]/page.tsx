"use client";

import { useParams } from "next/navigation";
import LearnMode from "../../_components/learn-mode/learn-mode";

export default function LearnPage() {
  const { id } = useParams<{ id: string }>();
  
  return <LearnMode />;
}