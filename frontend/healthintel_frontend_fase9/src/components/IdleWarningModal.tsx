import { Card, CardHeader } from './Card';
import { Button } from './Button';

interface IdleWarningModalProps {
  open: boolean;
  secondsLeft: number;
  onStay: () => void;
  onLogout: () => void;
}

export function IdleWarningModal({ open, secondsLeft, onStay, onLogout }: IdleWarningModalProps) {
  if (!open) return null;
  return (
    <div className="idle-modal-overlay" role="dialog" aria-modal="true" aria-labelledby="idle-modal-title">
      <Card className="modal-card idle-modal-card">
        <CardHeader
          title="Sessão prestes a expirar"
          description={`Por inatividade, você será desconectado em ${Math.max(secondsLeft, 0)}s.`}
        />
        <p id="idle-modal-title" className="idle-modal-hint">
          Clique em <strong>Continuar conectado</strong> para manter sua sessão ativa.
        </p>
        <div className="button-row">
          <Button onClick={onStay}>Continuar conectado</Button>
          <Button variant="secondary" onClick={onLogout}>Sair agora</Button>
        </div>
      </Card>
    </div>
  );
}
