// frontend/src/app/api/register/route.ts
import { PrismaClient } from "@prisma/client";
import bcrypt from "bcrypt";

const prisma = new PrismaClient();

export async function POST(req: Request) {
  try {
    const { email, password } = await req.json();

    // Vérifie si l'utilisateur existe déjà
    const existingUser = await prisma.user.findUnique({
      where: { email },
    });

    if (existingUser) {
      return new Response(JSON.stringify({ message: "Cet email est déjà utilisé." }), {
        status: 400,
      });
    }

    // Hash du mot de passe
    const hashedPassword = await bcrypt.hash(password, 10);

    // Crée un nouvel utilisateur
    const newUser = await prisma.user.create({
      data: {
        email,
        password: hashedPassword,
      },
    });

    return new Response(JSON.stringify({ user: newUser }), { status: 201 });
  } catch (error) {
    return new Response(JSON.stringify({ message: "Erreur interne." }), {
      status: 500,
    });
  }
}
