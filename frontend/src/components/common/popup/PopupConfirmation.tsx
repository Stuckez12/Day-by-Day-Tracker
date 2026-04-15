import "styles/common/popup/popup.scss";

import { confirmable, createConfirmation } from 'react-confirm';
import type { ConfirmDialog } from 'react-confirm';


export interface Props {
  okLabel?: string;
  cancelLabel?: string;
  title?: string;
  confirmation?: string;
};

const Confirmation: ConfirmDialog<Props, boolean> = (props) => (
  <div className="popup-background">
    <div className="popup-modal-container">
      <div className="modal-header">
        <div>{props.title}</div>
      </div>
      <div className="modal-body">
        {props.confirmation}
      </div>
      <div className="modal-footer">
        <button onClick={() => props.proceed(false)}>{props.cancelLabel || 'cancel'}</button>
        <button className="" onClick={() => props.proceed(true)}>{props.okLabel || 'ok'}</button>
      </div>
    </div>
  </div>
);

export const confirm = createConfirmation(confirmable(Confirmation));
