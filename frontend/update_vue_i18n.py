import os
import re

files_to_update = [
    'src/views/user/Dashboard.vue',
    'src/views/user/Detection.vue',
    'src/views/user/Traceability.vue',
    'src/views/user/Profile.vue',
    'src/views/admin/Dashboard.vue',
    'src/views/admin/Users.vue',
    'src/views/admin/Audit.vue'
]

# Quick mapping of English strings to i18n keys
replacements = {
    # Dashboard.vue
    'AI-powered image authentication and traceability system': "$t('dashboard.subtitle')",
    'Start Detection': "$t('dashboard.startDetection')",
    'Recent Detections': "$t('dashboard.recentDetections')",
    'View All': "$t('dashboard.viewAll')",
    'Image': "$t('common.image')",
    'Result': "$t('common.result')",
    'Confidence': "$t('common.confidence')",
    'Cert ID': "$t('common.certId')",
    'Date': "$t('common.date')",
    'Actions': "$t('common.actions')",
    'View Details': "$t('common.viewDetails')",
    'No detections yet': "$t('dashboard.noDetections')",
    'Fake': "$t('common.fake')",
    'Real': "$t('common.real')",
    
    # Detection.vue
    'Upload Image for Detection': "$t('detection.uploadTitle')",
    'Drop image here or <em>click to upload</em>': "$t('detection.dropOrClick')",
    'Supported formats: JPG, PNG, GIF (Max 10MB)': "$t('detection.supportedFormats')",
    'Cancel': "$t('common.cancel')",
    'Detection Results': "$t('detection.resultsTitle')",
    'New Detection': "$t('detection.newDetection')",
    'Original Image': "$t('detection.originalImage')",
    'Detection Heatmap': "$t('detection.heatmap')",
    '📊 Intelligent Analysis Report': "$t('detection.analysisReport')",
    'Verdict': "$t('detection.verdict')",
    'Risk Level': "$t('detection.riskLevel')",
    'Fake Probability': "$t('detection.fakeProbability')",
    'Summary': "$t('detection.summary')",
    'Detailed Analysis': "$t('detection.detailedAnalysis')",
    'Recommendations': "$t('detection.recommendations')",
    '🔐 Trusted Certification': "$t('detection.trustedCert')",
    'Certification ID': "$t('common.certId')",
    'SHA256 Hash': "$t('detection.sha256')",
    'Perceptual Hash': "$t('detection.phash')",
    'Signature': "$t('detection.signature')",
    'Verify Certification': "$t('detection.verifyCert')",
    'View Traceability': "$t('detection.viewTraceability')",

    # Traceability.vue
    'Traceability Report': "$t('traceability.reportTitle')",
    'Image Hash': "$t('traceability.imageHash')",
    'Blockchain Tx': "$t('traceability.blockchainTx')",
    'Timestamp': "$t('common.timestamp')",
    'Block Number': "$t('traceability.blockNumber')",
    'Verification Node': "$t('traceability.verificationNode')",
    'View on Explorer': "$t('traceability.viewOnExplorer')",

    # Profile.vue
    'User Profile': "$t('profile.title')",
    'Update Profile': "$t('profile.updateBtn')",
    'Change Password': "$t('profile.changePassword')",
    'Save Changes': "$t('common.save')",

    # Admin Dashboard
    "Today's Detections": "$t('adminDash.todayDetections')",
    "Today's Fake Count": "$t('adminDash.todayFakeCount')",
    "Today's Fake Ratio": "$t('adminDash.todayFakeRatio')",
    "Total Users": "$t('adminDash.totalUsers')",
    "Total Detections": "$t('adminDash.totalDetections')",
    "📊 Detection Statistics": "$t('adminDash.statsTitle')",
    "Fake Detection Rate": "$t('adminDash.fakeRate')",
    "🎯 Quick Actions": "$t('adminDash.quickActionsTitle')",
    "Manage Users": "$t('adminDash.manageUsers')",
    "View Audit Logs": "$t('adminDash.viewAuditLogs')",
    "Refresh Statistics": "$t('adminDash.refreshStats')",
    "📈 System Overview": "$t('adminDash.systemOverview')",
    "Today's Fake Images": "$t('adminDash.todayFakeImages')",
    "Today's Real Images": "$t('adminDash.todayRealImages')",
    "Fake Ratio": "$t('adminDash.fakeRatio')"
}

# Update files
for filepath in files_to_update:
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Use basic replace for templates where the text is inside tags
    for text, key in replacements.items():
        # Handle cases where text is between tags: >Text<
        content = content.replace(f'>{text}<', f'>{{{{ {key} }}}}<')
        # Handle cases where text is in a string prop: label="Text"
        content = content.replace(f'label="{text}"', f':label="{key}"')
        content = content.replace(f'title="{text}"', f':title="{key}"')
        content = content.replace(f'description="{text}"', f':description="{key}"')
        content = content.replace(f"'{text}'", f"{key}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Updated Vue files with i18n keys")
