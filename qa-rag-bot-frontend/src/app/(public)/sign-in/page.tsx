"use client";

import Link from "next/link";
import { motion } from "motion/react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useMutation } from "@tanstack/react-query";
// import { authQueryOptions } from "@/api-config/queryOptions/authQueries";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

export default function SignInPage() {
  const router = useRouter();

  const { mutate: loginMutate, isPending } = useMutation({
    // mutationFn: authQueryOptions.signInOptions.mutationFunction,
    // onSuccess: () => {
    //   toast.success("Signed in successfully!");
    //   router.push("/dashboard");
    // },
    // // eslint-disable-next-line @typescript-eslint/no-explicit-any
    // onError: (error: any) => {
    //   toast.error(`Sign in failed: ${error.response?.data?.message || error.message}`);
    // },
  })


  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);
    const signInData = {
      email: formData.get("email") as string,
      password: formData.get("password") as string,
    };
    // loginMutate({ body: signInData });
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-blue-50 to-red-50">
      <div className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center gap-10 px-6 py-12 sm:px-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="grid gap-12 rounded-3xl border border-gray-200 bg-white/80 p-8 shadow-xl backdrop-blur lg:grid-cols-[1.1fr_0.9fr]"
        >
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            className="space-y-6"
          >
            <p className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-4 py-1 text-xs uppercase tracking-[0.35em] text-blue-700">
              Welcome back
            </p>
            <h1 className="text-3xl font-semibold tracking-tight text-gray-900 sm:text-4xl">
              Sign in to your account
            </h1>
            <p className="text-base text-gray-600 sm:text-lg">
              Access your Rago dashboard to manage crawled content, track queries, and view analytics in real-time.
            </p>
            <div className="rounded-2xl border border-blue-200 bg-gradient-to-br from-blue-50 to-red-50 p-6 text-sm text-gray-700">
              <p className="text-xs uppercase tracking-[0.4em] text-gray-600">Why choose Rago</p>
              <ul className="mt-4 space-y-2">
                <li className="text-gray-700">🌐 Intelligent web crawling with advanced indexing.</li>
                <li className="text-gray-700">💡 AI-powered Q&A with relevant context.</li>
                <li className="text-gray-700">🔗 Multi-embedding support for better accuracy.</li>
              </ul>
            </div>
          </motion.div>

          <motion.form
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            onSubmit={handleSubmit}
            className="space-y-6 rounded-2xl border border-gray-200 bg-gradient-to-br from-gray-50 to-white p-6 shadow-lg"
          >
            <div className="flex flex-col space-y-2">
              <label htmlFor="email" className="text-sm font-medium text-gray-900">
                Email
              </label>
              <Input
                id="email"
                name="email"
                type="email"
                placeholder="you@company.com"
                required
                className="border-gray-300 bg-white text-gray-900 placeholder:text-gray-500"
              />
            </div>
            <div className="flex flex-col space-y-2">
              <label htmlFor="password" className="text-sm font-medium text-gray-900">
                Password
              </label>
              <Input
                id="password"
                name="password"
                type="password"
                placeholder="••••••••"
                required
                minLength={8}
                className="border-gray-300 bg-white text-gray-900 placeholder:text-gray-500"
              />
            </div>
            <div className="flex flex-wrap items-center justify-between gap-4 text-sm text-gray-600">
              <label className="inline-flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  id="remember"
                  name="remember"
                  className="size-4 rounded border border-gray-300 bg-white text-blue-600 accent-blue-600"
                />
                Remember me
              </label>
              <Link
                href="#"
                className="font-medium text-blue-600 transition hover:text-blue-700"
              >
                Forgot password?
              </Link>
            </div>
            <Button
              disabled={isPending}
              className="w-full bg-gradient-to-r from-blue-600 to-red-600 text-base text-white shadow-lg hover:shadow-xl hover:scale-105 transition-all"
            >
              {isPending ? "Signing in..." : "Sign in"}
            </Button>
            <p className="text-center text-sm text-gray-600">
              Don&apos;t have an account?{" "}
              <Link
                href="/sign-up"
                className="font-semibold text-blue-600 transition hover:text-blue-700"
              >
                Sign up here
              </Link>
            </p>
          </motion.form>
        </motion.div>
      </div>
    </div>
  );
}
