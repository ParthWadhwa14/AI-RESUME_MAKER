import React from 'react';
import { motion } from 'framer-motion';
import { LucideReact } from 'lucide-react';

export default function BentoProjects() {
 return (
 <motion.div
 initial={{ y: 20, opacity: 0 }}
 animate={{ y: 0, opacity: 1 }}
 transition={{ duration: 0.3 }}
 >
 <h2 className="text-3xl font-bold mb-4">Bento Projects</h2>
 <ul>
 <li>
 <LucideReact size={24} />
 Agentic RAG System
 </li>
 <li>
 <LucideReact size={24} />
 ResearchSync - AI-Powered Research Collaboration Platform
 </li>
 <li>
 <LucideReact size={24} />
 Network Intrusion Detection System
 </li>
 <li>
 <LucideReact size={24} />
 SehatSaathi-AI
 </li>
 <li>
 <LucideReact size={24} />
 Mental-Health-AI-Copilot
 </li>
 </ul>
 </motion.div>
 );
}