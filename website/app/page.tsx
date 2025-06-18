import Link from 'next/link'
import { motion } from 'framer-motion'
import { Rocket, Layers3, Cpu, Terminal } from 'lucide-react'
import Feature from '../components/Feature'
'use client';

const features = [
  {
    icon: <Layers3 size={32} />,
    title: 'Stack Clips Instantly',
    description: 'Combine talking head and gameplay footage into perfect 1080x1920 shorts.'
  },
  {
    icon: <Cpu size={32} />,
    title: 'GPU/CPU Support',
    description: 'Uses your GPU when available and gracefully falls back to CPU.'
  },
  {
    icon: <Terminal size={32} />,
    title: 'Local & Offline',
    description: 'Runs completely offline with whisper-based transcription.'
  }
]

export default function Home() {
  return (
    <main className="flex flex-col items-center px-6 py-12 space-y-12">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-5xl font-bold text-center">ShortSplit</h1>
        <p className="mt-4 text-center text-gray-600 text-lg max-w-2xl">
          Effortless vertical video stacking with automatic subtitles.
        </p>
      </motion.div>

      <div className="grid gap-8 sm:grid-cols-3">
        {features.map((f, i) => (
          <Feature key={i} icon={f.icon} title={f.title} description={f.description} />
        ))}
      </div>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
        <Link
          href="https://github.com/Dyhrrr/shortsplit"
          className="inline-flex items-center gap-2 rounded bg-black px-6 py-3 text-white hover:bg-gray-800"
        >
          <Rocket size={20} /> Get the Tool
        </Link>
      </motion.div>
    </main>
  )
}
