import { ReactNode } from 'react';

interface PageTransitionProps {
  children: ReactNode;
}

/**
 * A simple wrapper component with no transition effects.
 */
const PageTransition = ({ children }: PageTransitionProps) => {
  return <>{children}</>;
};

export default PageTransition;