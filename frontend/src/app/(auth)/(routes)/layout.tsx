// src/app/(auth)/(routes)/layout.tsx
const AuthLayout = (
    { children }: { children: React.ReactNode }
) => {
    return ( 
        <div className="h-full flex items-center justify-center">
            {children}
        </div>

     );
}
 
export default AuthLayout;