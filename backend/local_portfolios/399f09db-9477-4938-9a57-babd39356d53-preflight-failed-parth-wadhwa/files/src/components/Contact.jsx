import React from 'react';
import { motion } from 'framer-motion';
import { Mail, AiOutlinePhone } from 'lucide-react';

const Contact = () => {
 return (
 <section className="contact">
 <h2>Get in Touch</h2>
 <motion.div
 initial={{ opacity: 0 }}
 animate={{ opacity: 1 }}
 transition={{ duration: 0.3 }}
 >
 <p>
 <AiOutlineMail size={24} />
 <a href="mailto:parthwadhwa14@gmail.com">parthwadhwa14@gmail.com</a>
 </p>
 <p>
 <AiOutlinePhone size={24} />
 <a href="tel:+91 1234567890">+91 1234567890</a>
 </p>
 </motion.div>
 </section>
 );
};

export default Contact;
