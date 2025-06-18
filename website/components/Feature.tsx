import { motion } from 'framer-motion'
import { ReactNode } from 'react'

interface FeatureProps {
  icon: ReactNode
  title: string
  description: string
}

export default function Feature({ icon, title, description }: FeatureProps) {
  return (
    <motion.div
      className="flex flex-col items-center text-center space-y-2"
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
    >
      <div className="text-primary-500">{icon}</div>
      <h3 className="text-xl font-semibold">{title}</h3>
      <p className="text-gray-600 max-w-xs">{description}</p>
    </motion.div>
  )
}
