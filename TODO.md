# Workout PDF Export Enhancement - TODO

## Completed
- Analyzed the current PDF export implementation in workouts/views.py
- Created a detailed plan to improve PDF styling and layout
- Implemented enhancements to workout_export_pdf function:
  - Centered, larger, bold title with separator line
  - Bold section headers and key labels for clarity
  - Added spacing and line breaks for readability
  - Drawn border boxes around individual exercises to separate visually
  - Improved font sizes and consistent styling throughout PDF

## Next Steps
- Test the PDF export functionality to verify improved look
- Gather feedback for further tweaks or adjustments if needed
- Optionally add footers, page numbers, or color styles in future enhancements

# Add Bootstrap Video Modals to Workout Detail Template

## Completed
- [x] Update Demo button in `workout_detail.html` to trigger modal (replace <a> link)
- [x] Add conditional Bootstrap 5 modals with responsive video players inside the exercise loop

## Next Steps
- [ ] Test: Runserver, check modal opens/closes, video plays responsively, unique IDs work (requires workout with exercises having video_url)
- [x] Mark implementation as completed in TODO.md
