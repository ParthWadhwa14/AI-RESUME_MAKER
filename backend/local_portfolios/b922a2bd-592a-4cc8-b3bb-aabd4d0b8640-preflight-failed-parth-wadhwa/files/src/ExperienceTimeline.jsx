import React from 'react';
import { motion } from 'framer-motion';
import { LucideNodejs } from 'lucide-react';

export default function ExperienceTimeline() {
 return (
 <motion.div
 initial={{ y: 20, opacity: 0 }}
 animate={{ y: 0, opacity: 1 }}
 transition={{ duration: 0.3 }}
 >
 <h2 className="text-3xl font-bold mb-4">Experience Timeline</h2>
 <ul>
 <li>
 <LucideNodejs size={24} />
 AI Intern at Fumind.ai (Feb - April 2026)
 </li>
 </ul>
 </motion.div>
 );
}