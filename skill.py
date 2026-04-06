import base64
from googleapiclient.http import MediaInMemoryUpload

def run(command, args, context):
    gmail = context.get_tool("gog").gmail
    drive = context.get_tool("gog").drive

    query = []

    if args.get("from"):
        query.append(f'from:{args["from"]}')
    if args.get("subject"):
        query.append(f'subject:{args["subject"]}')
    if args.get("newer_than"):
        query.append(f'newer_than:{args["newer_than"]}')

    # 메일 ID 직접 지정
    if args.get("id"):
        message_id = args["id"]
    else:
        q = " ".join(query)
        messages = gmail.list_messages(q)
        if not messages:
            return "메일을 찾지 못했습니다."
        message_id = messages[0]["id"]

    message = gmail.get_message(message_id)

    if "parts" not in message["payload"]:
        return "첨부파일이 없습니다."

    attachments = []
    for part in message["payload"]["parts"]:
        if part.get("filename"):
            attachment_id = part["body"]["attachmentId"]
            data = gmail.get_attachment(message_id, attachment_id)
            file_data = base64.urlsafe_b64decode(data["data"])
            attachments.append((part["filename"], file_data))

    if not attachments:
        return "첨부파일이 없습니다."

    folder_path = args["save_to"]

    for filename, file_data in attachments:
        media = MediaInMemoryUpload(file_data)
        drive.upload_file(
            name=filename,
            folder_path=folder_path,
            media_body=media
        )

    return f"{len(attachments)}개의 첨부파일을 '{folder_path}'에 저장했습니다."
