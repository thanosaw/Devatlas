import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import SidePanel from "./components/SidePanel";
import Image from "next/image";
import Link from "next/link";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Your App Name",
  description: "Your app description",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // Define the icons for the side panel using SVGs from public/icons folder with routing
  const sideIcons = [
    <Link key="logo" href="/" prefetch={false} replace={true}>
      <Image src="/icons/logo.svg" alt="Home" width={32} height={32} priority />
    </Link>,
    <Image key="add" src="/icons/add.svg" alt="Add" width={32} height={32} />,
    <Image key="side" src="/icons/side.svg" alt="Side" width={32} height={32} />,
    <Link key="people" href="/developers" prefetch={false}>
      <Image src="/icons/people.svg" alt="Developers" width={32} height={32} />
    </Link>,
    <Link key="graph" href="/graph" prefetch={false}>
      <Image src="/icons/graph.svg" alt="Graph" width={32} height={32} />
    </Link>
  ];

  // Bottom icon path (you'll need to add this image to your public folder)
  const bottomIconPath = "/icons/daniel.png";

  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="flex">
          <SidePanel topIcons={sideIcons} bottomIcon={bottomIconPath} />
          <main className="ml-[70px] w-[calc(100%-70px)]">{children}</main>
        </div>
      </body>
    </html>
  );
} 