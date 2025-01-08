import Image from "next/image";

export const Logo = () => {
    return (
        <Image className="border border-gray-100 rounded-lg center-align center-block"
            height={75}
            width={75}
            alt="Logo"
            src="/logo1.svg"
        />
    );
}
