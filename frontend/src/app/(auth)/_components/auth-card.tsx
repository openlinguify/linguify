import { Card, CardContent, CardHeader } from "@/shared/components/ui/card";

interface AuthCardProps {
  children: React.ReactNode;
}

export function AuthCard({ children }: AuthCardProps) {
  return (
    <Card className="w-full max-w-md shadow-lg border-gray-100">
      <CardContent className="p-0">
        {children}
      </CardContent>
    </Card>
  );
}

export function AuthCardHeader({ children }: { children: React.ReactNode }) {
  return (
    <CardHeader className="pb-8 pt-6 px-6 text-center space-y-1">
      {children}
    </CardHeader>
  );
}

export function AuthCardContent({ children }: { children: React.ReactNode }) {
  return (
    <CardContent className="px-6 pb-6 pt-2">
      {children}
    </CardContent>
  );
}