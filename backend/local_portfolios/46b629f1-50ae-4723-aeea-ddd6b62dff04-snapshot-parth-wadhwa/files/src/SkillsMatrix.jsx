import React from 'react';
import { motion } from 'framer-motion';
import { LucideGraph } from 'lucide-react';

export default function SkillsMatrix() {
 return (
 <motion.div
 initial={{ y: 20, opacity: 0 }}
 animate={{ y: 0, opacity: 1 }}
 transition={{ duration: 0.3 }}
 >
 <h2 className="text-3xl font-bold mb-4">Skills Matrix</h2>
 <ul>
 <li>
 <LucideGraph size={24} />
 Frontend:
 <ul>
 <li>React</li>
 <li>JavaScript</li>
 </ul>
 </li>
 <li>
 <LucideGraph size={24} />
 Backend:
 <ul>
 <li>Node.js</li>
 <li>Python</li>
 </ul>
 </li>
 <li>
 <LucideGraph size={24} />
 AI/ML:
 <ul>
 <li>LangGraph</li>
 <li>OpenAI API / SDK</li>
 </ul>
 </li>
 <li>
 <LucideGraph size={24} />
 Tools:
 <ul>
 <li>Git</li>
 <li>GitHub</li>
 </ul>
 </li>
 </ul>
 </motion.div>
 );
}