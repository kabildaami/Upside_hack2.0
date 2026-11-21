export default function EncouragementBanner({ message }) {
  if (!message) return null;
  return <div className="private-win">Private progress: {message}</div>;
}
