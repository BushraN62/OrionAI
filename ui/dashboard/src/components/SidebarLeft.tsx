import { motion } from 'framer-motion';
import { SessionList } from './SessionList';

export function SidebarLeft() {
  return (
    <motion.aside
      initial={{ x: -30, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className="h-full border-r border-slate-800/80 shadow-2xl overflow-hidden"
    >
      <SessionList />
    </motion.aside>
  );
}
