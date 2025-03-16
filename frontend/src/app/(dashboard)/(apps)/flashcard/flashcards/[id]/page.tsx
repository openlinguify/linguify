"use client";

import { useParams } from "next/navigation";
import FlashcardApp from "../../_components/FlashCards";

export default function FlashcardsPage() {
  const { id } = useParams<{ id: string }>();
  
  return <FlashcardApp />;
}
