"use client";

import { useParams } from "next/navigation";
import ReviewMode from "../../_components/review-mode/review-mode";

export default function ReviewPage() {
  const { id } = useParams<{ id: string }>();
  
  return <ReviewMode />;
}