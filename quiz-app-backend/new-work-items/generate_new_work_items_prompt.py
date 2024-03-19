import pandas as pd

def convert_csv_to_markdown(csv_file_path, template_file_path, output_file_path):
    # Load the CSV
    csv_data = pd.read_csv(csv_file_path)
    
    # Sort the dataframe by Work Item Type and then by ID
    csv_data_sorted = csv_data.sort_values(by=['Work Item Type', 'ID'], ascending=[False, True])
    
    # Function to convert a row to markdown section
    def row_to_markdown(row):
        md = f"### {row['Title']}\n\n"
        md += f"**ID:** {row['ID']}\n\n"
        md += f"**Work Item Type:** {row['Work Item Type']}\n\n"
        md += f"**State:** {row['State']}\n\n"
        md += f"**Tags:** {row['Tags']}\n\n"
        if pd.notnull(row['Description']):
            md += f"**Description:**\n\n{row['Description']}\n\n"
        if pd.notnull(row['Acceptance Criteria']):
            # Splitting the acceptance criteria by newline and converting to bullet points
            criteria_list = row['Acceptance Criteria'].split('\n')
            criteria_md = '\n'.join([f"- {item}" for item in criteria_list if item.strip() != ''])
            md += f"**Acceptance Criteria:**\n\n{criteria_md}\n\n"
        return md

    # Applying the conversion function to each row
    markdown_sections = csv_data_sorted.apply(row_to_markdown, axis=1)
    
    # Combining all sections into one markdown string
    markdown_content = "\n".join(markdown_sections)
    
    # Load the markdown template
    with open(template_file_path, 'r') as file:
        template_content = file.read()
    
    # Replace the placeholder with the actual markdown content
    final_markdown = template_content.replace('<details from /code/quiz-app/quiz-app-backend/new-work-items/new-work-items.csv>', markdown_content)
    
    # Saving the combined markdown output
    with open(output_file_path, 'w') as file:
        file.write(final_markdown)
    
    print(f"Markdown document saved to {output_file_path}")

# Example usage:
if __name__ == "__main__":
    csv_file_path = '/code/quiz-app/quiz-app-backend/new-work-items/new-work-items.csv'
    template_file_path = '/code/quiz-app/quiz-app-backend/new-work-items/new-work-items-prompt-template.md'
    output_file_path = '/code/quiz-app/quiz-app-backend/new-work-items/new-work-items-prompt.md'
    convert_csv_to_markdown(csv_file_path, template_file_path, output_file_path)
