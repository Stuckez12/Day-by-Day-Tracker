import { confirmable, createConfirmation } from "react-confirm";
import type { ConfirmDialog } from "react-confirm";

import type { PopupConfirmProps } from "interfaces/common/popup/popup";

import "styles/common/form-inputs.scss";
import "styles/common/popup/popup.scss";

// eslint-disable-next-line react-refresh/only-export-components
const Confirmation: ConfirmDialog<PopupConfirmProps, boolean> = (props) => (
  <div className="popup-background">
    <div className="popup-container">
      <div className="popup-header">
        <h1>{props.title}</h1>
      </div>
      <div className="popup-body">
        <p>{props.text_body}</p>
      </div>
      <div className="popup-footer">
        <button className="action-button" onClick={() => props.proceed(false)}>
          {props.cancel_label || "Cancel"}
        </button>
        <button className="action-button" onClick={() => props.proceed(true)}>
          {props.proceed_label || "Continue"}
        </button>
      </div>
    </div>
  </div>
);

export const confirm = createConfirmation(confirmable(Confirmation));
