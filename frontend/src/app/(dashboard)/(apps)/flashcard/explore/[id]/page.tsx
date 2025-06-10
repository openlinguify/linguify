// app/flashcard/explore/[id]/page.tsx
import PublicDeckDetail from '@/addons/flashcard/components/public/PublicDeckDetail';

export default async function DeckDetailPage({ params }: { params: Promise<{ id: string }> }) {
    const { id } = await params;
    return <PublicDeckDetail deckId={parseInt(id)} />;
}