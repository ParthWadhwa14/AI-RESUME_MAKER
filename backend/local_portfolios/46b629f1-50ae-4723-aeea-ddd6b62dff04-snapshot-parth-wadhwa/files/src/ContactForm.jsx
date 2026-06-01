import React from 'react';
import { motion } from 'framer-motion';
import { LucideAi } from 'lucide-react';

export default function ContactForm() {
 return (
 <motion.div
 initial={{ y: 20, opacity: 0 }}
 animate={{ y: 0, opacity: 1 }}
 transition={{ duration: 0.3 }}
 >
 <h2 className="text-3xl font-bold mb-4">Get in Touch</h2>
 <p className="text-lg mb-4">Let's discuss how I can help you with your AI and full-stack development needs</p>
 <form>
 <label>
 <LucideAi size={24} />
 Name:
 <input type="text" className="px-4 py-2 rounded-md" />
 </label>
 <label>
 <LucideAi size={24} />
 Email:
 <input type="email" className="px-4 py-2 rounded-md" />
 </label>
 <label>
 <LucideAi size={24} />
 Message:
 <textarea className="px-4 py-2 rounded-md" />
 </label>
 <button className="bg-primary hover:bg-secondary text-text px-4 py-2 rounded-md">
 <LucideAi size={24} />
 Send
 </button>
 </form>
 </motion.div>
 );
}