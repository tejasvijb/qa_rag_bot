"use client";
import Link from "next/link";
import { motion } from "motion/react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useMutation } from "@tanstack/react-query";
// import { authQueryOptions } from "@/api-config/queryOptions/authQueries";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

export default function SignUpPage() {
  const router = useRouter();

  const { mutate: signUpMutate, isPending } = useMutation({
    // mutationFn: authQueryOptions.signUpOptions.mutationFunction,
    // onSuccess: () => {
    //   toast.success("Signed up successfully! Please sign in.");
    //   router.push("/sign-in");
    // },
    // // eslint-disable-next-line @typescript-eslint/no-explicit-any
    // onError: (error: any) => {
    //   toast.error(`Sign up failed: ${error.response?.data?.message || error.message}`);
    // },

  });



  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);
    const password = formData.get("password") as string;
    const confirmPassword = formData.get("confirmPassword") as string;

    if (password !== confirmPassword) {
      toast.error("Passwords do not match");
      return;
    }

    const signUpData = {
      firstName: formData.get("firstName") as string,
      lastName: formData.get("lastName") as string,
      email: formData.get("email") as string,
      password: password,
    };

    // signUpMutate({ body: signUpData });


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
            <p className="inline-flex items-center gap-2 rounded-full border border-red-200 bg-red-50 px-4 py-1 text-xs uppercase tracking-[0.35em] text-red-700">
              Welcome to Rago
            </p>
            <h1 className="text-3xl font-semibold tracking-tight text-gray-900 sm:text-4xl">
              Create an account
            </h1>
            <p className="text-base text-gray-600 sm:text-lg">
              Start leveraging AI-powered Q&A for your web content. Crawl websites, get contextual answers, and combine multiple embeddings for superior results.
            </p>
            <div className="rounded-2xl border border-red-200 bg-gradient-to-br from-red-50 to-blue-50 p-6">
              <p className="text-xs uppercase tracking-[0.4em] text-gray-600">What you get</p>
              <div className="mt-4 grid gap-3 text-sm text-gray-700">
                <p>• Intelligent website crawling and content indexing.</p>
                <p>• Advanced Q&A with contextual understanding.</p>
                <p>• Real-time analytics and usage tracking.</p>
              </div>
            </div>
          </motion.div>

          <motion.form
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
            onSubmit={handleSubmit}
            className="space-y-6 rounded-2xl border border-gray-200 bg-gradient-to-br from-gray-50 to-white p-6 shadow-lg"
          >
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="flex flex-col space-y-2">
                <label htmlFor="first-name" className="text-sm font-medium text-gray-900">
                  First name
                </label>
                <Input
                  id="first-name"
                  name="firstName"
                  placeholder="Alex"
                  required
                  className="border-gray-300 bg-white text-gray-900 placeholder:text-gray-500"
                />
              </div>
              <div className="flex flex-col space-y-2">
                <label htmlFor="last-name" className="text-sm font-medium text-gray-900">
                  Last name
                </label>
                <Input
                  id="last-name"
                  name="lastName"
                  placeholder="Rivera"
                  required
                  className="border-gray-300 bg-white text-gray-900 placeholder:text-gray-500"
                />
              </div>
            </div>
            <div className="flex flex-col space-y-2">
              <label htmlFor="signup-email" className="text-sm font-medium text-gray-900">
                Email address
              </label>
              <Input
                id="signup-email"
                name="email"
                type="email"
                placeholder="you@company.com"
                required
                className="border-gray-300 bg-white text-gray-900 placeholder:text-gray-500"
              />
            </div>
            <div className="flex flex-col space-y-2">
              <label htmlFor="signup-password" className="text-sm font-medium text-gray-900">
                Password
              </label>
              <Input
                id="signup-password"
                name="password"
                type="password"
                placeholder="Create a strong password"
                required
                minLength={8}
                className="border-gray-300 bg-white text-gray-900 placeholder:text-gray-500"
              />
            </div>
            <div className="flex flex-col space-y-2">
              <label htmlFor="confirm-password" className="text-sm font-medium text-gray-900">
                Confirm password
              </label>
              <Input
                id="confirm-password"
                name="confirmPassword"
                type="password"
                placeholder="Re-enter password"
                required
                minLength={8}
                className="border-gray-300 bg-white text-gray-900 placeholder:text-gray-500"
              />
            </div>
            <label className="flex items-start gap-3 text-sm text-gray-600 cursor-pointer">
              <input
                type="checkbox"
                id="terms"
                name="terms"
                required
                className="mt-1 size-4 rounded border border-gray-300 bg-white text-red-600 accent-red-600"
              />
              <span>
                I agree to the{" "}
                <Link href="#" className="font-medium text-red-600 transition hover:text-red-700">
                  Terms &amp; Conditions
                </Link>
                , including the privacy policy.
              </span>
            </label>
            <Button
              disabled={isPending}
              type="submit"
              className="w-full bg-gradient-to-r from-blue-600 to-red-600 text-base text-white shadow-lg hover:shadow-xl hover:scale-105 transition-all"
            >
              {isPending ? "Creating account..." : "Create account"}
            </Button>
            <p className="text-center text-sm text-gray-600">
              Already have an account?{" "}
              <Link
                href="/sign-in"
                className="font-semibold text-blue-600 transition hover:text-blue-700"
              >
                Sign in here
              </Link>
            </p>
          </motion.form>
        </motion.div>
      </div>
    </div>
  );
}
