import { NextResponse } from 'next/server';

export async function GET() {
    return NextResponse.json({ test: 'Hello from the API' });
}

export async function getServerSideProps() {
    // Appel à l'API des cours
    const courseResponse = await fetch('http://127.0.0.1:8000/api/course/');
    const courses = await courseResponse.json();

    // Appel à l'API d'authentification
    const authResponse = await fetch('http://127.0.0.1:8000/api/authentication/');
    const authentication = await authResponse.json();

    return {
        props: {
            courses,
            authentication,
        },
    };
}
