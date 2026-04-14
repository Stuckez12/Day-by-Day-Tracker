import "styles/common/popup/popup.scss";

interface PopupButtonProps {
  text: string;
}

interface PopupConfirmationProps {
  url: string;
  message: string;
  confirm_button_first: boolean;
  confirm_button: PopupButtonProps;
  deny_button: PopupButtonProps;
}

function PopupConfirmation({ url, message, confirm_button_first, confirm_button, deny_button }: PopupConfirmationProps) {
  return (
    <div className="popup-background">
      <div className="popup-modal">
        <p>URL: {url}</p><br/>
        <p>Message: {message}</p><br/>
        <p>Confirm button first: {confirm_button_first}</p><br/>
        <p>Confirm text: {confirm_button.text}</p><br/>
        <p>Deny text: {deny_button.text}</p>
      </div>
    </div>
  );
}

export default PopupConfirmation;
