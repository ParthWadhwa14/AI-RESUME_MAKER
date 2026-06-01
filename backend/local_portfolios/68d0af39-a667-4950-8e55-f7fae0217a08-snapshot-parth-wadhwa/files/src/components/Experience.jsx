import React from 'react';
import { motion } from 'framer-motion';

export default function Experience() {
 return (
 <section className="experience flex flex-col items-center py-4">
 <h1 className="text-3xl font-bold">Experience</h1>
 <motion.div
 initial={{ opacity: 0 }}
 animate={{ opacity: 1 }}
 transition={{ duration: 0.5 }}
 >
 <p className="text-2xl">AI Intern at Fumind.ai (Feb - April 2026)</p>
 <ul className="list-disc ml-4">
 <li className="text-lg">Built a one-shot image segmentation pipeline using OpenCV and vision-language models</li>
 <li className="text-lg">Worked on AI-assisted computer vision workflows</li>
 <li className="text-lg">Integrated the system into the company monorepo</li>
 <li className="text-lg">Collaborated in a fast-paced development environment</li>
 </ul>
 </motion.div>
 </section>
 );
}
