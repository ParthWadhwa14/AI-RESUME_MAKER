import React from 'react';
import { motion } from 'framer-motion';
import { LucideReact } from 'lucide-react';

export default function Home() {
 return (
 <motion.div
 initial={{ y: 20, opacity: 0 }}
 animate={{ y: 0, opacity: 1 }}
 transition={{ duration: 0.3 }}
 >
 <h1 className="text-5xl font-bold mb-4">Parth Wadhwa - AI Full-Stack Developer</h1>
 <p className="text-lg mb-4">Building innovative AI solutions with a passion for full-stack development</p>
 <button className="bg-primary hover:bg-secondary text-text px-4 py-2 rounded-md">
 <LucideReact size={24} />
 Explore My Projects
 </button>
 </motion.div>
 );
}