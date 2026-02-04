"use client";

import { useRouter } from "next/navigation";
// import { useAuth } from "../hooks/useAuth";
import { ReactNode, useEffect } from "react";

export default function AuthLayout({ children }: { children: ReactNode }) {
  const router = useRouter();
  // const { isCurrentUserAuthenticated } = useAuth();


  // useEffect(() => {
  //   if (isCurrentUserAuthenticated) {
  //     router.push("/dashboard");
  //   }
  // }, [isCurrentUserAuthenticated, router]);

  return <div>{children}</div>;

}