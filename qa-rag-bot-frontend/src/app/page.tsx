"use client";

import { Button } from "@/components/ui/button";
import Link from "next/link";
import { motion } from "motion/react";
import { Globe, MessageSquare, Network } from "lucide-react";

export default function Home() {
  const features = [
    {
      icon: Globe,
      title: "Crawls Websites",
      description:
        "Intelligently extracts and indexes content from websites to build a comprehensive knowledge base.",
    },
    {
      icon: MessageSquare,
      title: "Answers with Context",
      description:
        "Provides accurate answers to user queries with relevant context from the crawled data.",
    },
    {
      icon: Network,
      title: "Multiple Embeddings",
      description:
        "Combines multiple embeddings for enhanced understanding and more accurate response generation.",
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.8 },
    },
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-blue-50 to-red-50 text-gray-900">
      {/* Header */}
      <header className="sticky top-0 z-50 backdrop-blur-sm bg-white/80 border-b border-gray-200">
        <div className="mx-auto max-w-6xl px-6 py-4 sm:px-10 flex items-center justify-between">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="text-2xl font-bold"
          >
            <span className="text-red-600">Ra</span>
            <span className="text-blue-600">go</span>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="flex items-center gap-3"
          >
            <Button
              variant="ghost"
              className="text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors"
              asChild
            >
              <Link href="/sign-in">Sign in</Link>
            </Button>
            <Button
              className="bg-gradient-to-r from-blue-600 to-red-600 text-white shadow-lg hover:shadow-xl hover:scale-105 transition-all"
              asChild
            >
              <Link href="/sign-up">Sign up</Link>
            </Button>
          </motion.div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="mx-auto max-w-6xl px-6 py-20 sm:px-10">
        <motion.div
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-12"
        >
          <h1 className="text-5xl sm:text-6xl font-bold mb-6">
            <span className="bg-gradient-to-r from-blue-600 via-red-600 to-blue-600 bg-clip-text text-transparent">
              Intelligent Q&A
            </span>
            <br />
            <span className="text-gray-800">for Your Web Content</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Rago crawls websites, understands context, and delivers accurate
            answers using advanced embedding technology.
          </p>
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="flex gap-4 justify-center flex-wrap"
          >
            <Button
              className="bg-gradient-to-r from-blue-600 to-red-600 text-white px-8 py-3 text-lg hover:shadow-xl hover:scale-105 transition-all"
              asChild
            >
              <Link href="/sign-up">Get Started</Link>
            </Button>
            <Button
              variant="outline"
              className="border-2 border-blue-600 text-blue-600 hover:bg-blue-50 px-8 py-3 text-lg transition-all"
              asChild
            >
              <Link href="#features">Learn More</Link>
            </Button>
          </motion.div>
        </motion.div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white border-y border-gray-200">
        <div className="mx-auto max-w-6xl px-6 sm:px-10">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl sm:text-5xl font-bold mb-4">
              Powerful Features
            </h2>
            <p className="text-xl text-gray-600">
              Everything you need for intelligent web content analysis
            </p>
          </motion.div>

          <motion.div
            variants={containerVariants}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true }}
            className="grid md:grid-cols-3 gap-8"
          >
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={index}
                  variants={itemVariants}
                  className="p-8 rounded-2xl border-2 border-gray-200 hover:border-blue-500 transition-all hover:shadow-lg hover:scale-105 bg-gradient-to-br from-gray-50 to-white"
                >
                  <motion.div
                    initial={{ scale: 0 }}
                    whileInView={{ scale: 1 }}
                    transition={{ delay: 0.2 + index * 0.1, duration: 0.5 }}
                    viewport={{ once: true }}
                    className="w-12 h-12 rounded-lg bg-gradient-to-br from-blue-500 to-red-500 flex items-center justify-center mb-4"
                  >
                    <Icon className="w-6 h-6 text-white" />
                  </motion.div>
                  <h3 className="text-xl font-bold mb-3 text-gray-900">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">
                    {feature.description}
                  </p>
                </motion.div>
              );
            })}
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-red-600">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          viewport={{ once: true }}
          className="mx-auto max-w-4xl px-6 sm:px-10 text-center text-white"
        >
          <h2 className="text-4xl sm:text-5xl font-bold mb-6">
            Ready to Get Started?
          </h2>
          <p className="text-xl mb-8 opacity-95">
            Join thousands of users leveraging AI-powered Q&A for their content
          </p>
          <Button
            className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-3 text-lg font-semibold hover:scale-105 transition-all"
            asChild
          >
            <Link href="/sign-up">Start Free Trial</Link>
          </Button>
        </motion.div>
      </section>
    </div>
  );
}
