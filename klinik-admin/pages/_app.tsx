import type { AppProps } from "next/app";
import Head from "next/head";
import { Geist, Geist_Mono } from "next/font/google";

import "@/styles/globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export default function App({ Component, pageProps }: AppProps) {
  return (
    <div className={`${geistSans.variable} ${geistMono.variable} flex flex-1 flex-col`}>
      <Head>
        <title>Klinik Admin</title>
        <meta name="description" content="Klinik Admin" />
      </Head>
      <Component {...pageProps} />
    </div>
  );
}
