import csv
import os
import subprocess
import pandas as pd
import json

# Function to get Radon Cyclomatic Complexity in JSON format
def get_radon_cc_json(repo_dir):
    try:
        result = subprocess.run(
            ["radon", "cc", repo_dir, "--json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            timeout = 30
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, Exception) as e:
        #print(f"Error getting Cyclomatic Complexity for {repo_dir}: {e.stderr}")
        return None

def get_raw_metrics(repo_dir):
        try:
            result = subprocess.run(
                ["radon", "raw", repo_dir, "--json"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True.as_integer_ratio,
                timeout = 30
            )
            
            return json.loads(result.stdout)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(f"Error getting Raw metrics for {repo_dir}: {e.stderr}")
            return None

# Function to get Radon Halstead metrics (volume, difficulty, effort)
def get_halstead_metrics(repo_dir):
    print(repo_dir)
    try:
        result = subprocess.run(
            ["radon", "hal", repo_dir, "--json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            timeout = 30
        )

        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"Error getting Halstead metrics for {repo_dir}: {e.stderr}")
        return None

# Function to get Radon Maintainability Index
def get_maintainability_index(repo_dir):
    try:
        result = subprocess.run(
            ["radon", "mi", repo_dir, "--json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            timeout=30
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f"Error getting Maintainability Index for {repo_dir}: {e.stderr}")
        return None

def process_repositories(csv_file):
    # Read the CSV file using pandas
    repos_df = pd.read_csv(csv_file)

    # Loop over each row (repository)
    for index, row in repos_df.iterrows():
        repo_url = row["URL"]
        repo_name = row["Repository"]
        repo_stars = row["Stars"]
        repo_forks = row["Forks"]
        repo_search = row["SearchedBy"]
        repo_order = row["Order"]

        # Clone or pull the repository
        repo_dir = f"temp_repos/{repo_name}"
        if not os.path.exists(repo_dir):
            os.makedirs(repo_dir)
            try:
                subprocess.run(["git", "clone", repo_url, repo_dir], check=True, timeout=90)
            except:
                print(f"Cloning of {repo_url} timed out after 90 seconds. Killing process.")
                continue
        else:
            try:
                subprocess.run(["git", "-C", repo_dir, "pull"], check=True, timeout=90)

            except:
                print(f"Cloning of {repo_url} timed out after 90 seconds. Killing process.")
                continue

        print('Extracting repo ' + repo_dir)
        # Request Radon JSON output and process Cyclomatic Complexity
        cc_data = get_radon_cc_json(repo_dir)
        if cc_data:
            print(f"Debug: cc_data for {repo_name}:", cc_data)  # Debugging line to inspect the structure

            total_cc = 0
            avg_cc = 0
            cc_scores = []
            # Look through the JSON and check for the correct key
            for filename, metrics in cc_data.items():
                for metric in metrics:
                    print(f"Debug: Metric for {filename}: {metric}")  # Debugging line to check the contents of each metric
                    # Look for the 'complexity' key and append the value
                    if 'complexity' in metric:
                        cc_scores.append(metric['complexity'])  # Use 'complexity' instead of 'cc'
                    else:
                        print(f"Warning: 'complexity' key not found in metric for {filename}")  # Handle missing 'complexity' key
            total_cc = sum(cc_scores)
            avg_cc = total_cc / len(cc_scores) if cc_scores else 0
             
            raw_data = get_raw_metrics(repo_dir)
            if raw_data:
                #Set the list values for each metric needed
                sloc_vals = []
                lloc_vals = []
                comment_vals = []
                blank_vals = []
                multi_vals = []
                #access and store metrics to lists
                for file_title, values in raw_data.items():
                    print(values)
                    if 'sloc' in values:
                        sloc_vals.append(values['sloc'])
                    else:
                        sloc_vals.append(0)
                    if 'lloc' in values:
                        lloc_vals.append(values['lloc'])
                    else:
                        lloc_vals.append(0)
                    if 'comments' in values:
                        comment_vals.append(values['comments'])
                    else:
                        comment_vals.append(0)
                    if 'blank' in values:
                        blank_vals.append(values['blank'])
                    else:
                        blank_vals.append(0)
                    if 'multi' in values:
                        multi_vals.append(values['multi'])
                    else:
                        multi_vals.append(0)
                #Calculate total Values
                total_sloc = sum(sloc_vals)
                total_lloc = sum(lloc_vals)
                total_comment = sum(comment_vals)
                total_blank = sum(blank_vals)
                total_multi = sum(multi_vals)
                #Calculate Average values 
                avg_sloc = total_sloc/len(sloc_vals)
                avg_lloc = total_lloc/len(lloc_vals)
                avg_comment = total_comment/len(comment_vals)
                avg_blank = total_blank/len(blank_vals)
                avg_multi = total_multi/len(multi_vals)

            # Request Radon Halstead metrics
            halstead_data = get_halstead_metrics(repo_dir)

            hal_volumes = []
            hal_diff = []
            hal_effort = []
            hal_time = []
            hal_bugs = []
            files_ignored = 0
            if halstead_data:
                for hal_file, hal_vals in halstead_data.items():
                    print('+++++++++++++++++++++++++')
                    print(hal_vals)
                    if 'total' in hal_vals:
                        halstead_access = hal_vals['total']
                        hal_volumes.append(halstead_access['volume'])
                        hal_diff.append(halstead_access['difficulty'])
                        hal_effort.append(halstead_access['effort'])
                        hal_time.append(halstead_access['time'])
                        hal_bugs.append(halstead_access['bugs'])
                    else:
                        files_ignored +=1
                #Calculate totals
                hal_vol_tot = sum(hal_volumes)
                hal_diff_tot = sum(hal_diff)
                hal_effort_tot = sum(hal_effort)
                hal_time_tot = sum(hal_time)
                hal_bugs_tot = sum(hal_bugs)
                #Calculate Averages
                if len(hal_volumes) > 0:
                    hal_vol_avg = hal_vol_tot/len(hal_volumes)
                else:
                    hal_vol_avg = hal_vol_tot
                if len(hal_diff) > 0:
                    hal_diff_avg = hal_diff_tot/len(hal_diff)
                else:
                    hal_diff_avg = hal_diff_tot
                if len(hal_effort) > 0:
                    hal_effort_avg = hal_effort_tot/len(hal_effort)
                else:
                    hal_effort_avg = hal_effort_tot
                if len(hal_time) > 0:
                    hal_time_avg = hal_time_tot/len(hal_time)
                else:
                    hal_time_avg = hal_time_tot
                if len(hal_bugs) > 0:
                    hal_bugs_avg = hal_bugs_tot/len(hal_bugs)
                else:
                    hal_bugs_avg = hal_bugs_tot

            else:
                hal_vol_avg = hal_diff_avg = hal_effort_avg = hal_time_avg = hal_bugs_avg = 0 
            

            # Request Radon Maintainability Index
            maintainability_scores = []
            maintainability_data = get_maintainability_index(repo_dir)
            #print(maintainability_data)
            if maintainability_data:
                for file, dataInfo in maintainability_data.items():
                    #print('++++++++++++++++++++++++++++++++++')
                    #print(dataInfo)
                    if 'mi' in dataInfo:
                        maintainability_scores.append(dataInfo['mi'])
                avg_mi = sum(maintainability_scores) / len(maintainability_scores) if maintainability_scores else 0
            else:
                avg_mi = 'Error'

            # Update the dataframe with the new metrics
            new_row = {
                "URL": repo_url,
                "Repository": repo_name,
                "Stars": repo_stars,
                "Forks": repo_forks,
                "Search_by": repo_search,
                "Search_order": repo_order,
                "avg_cc": avg_cc,
                "total_cc": total_cc,
                "Avg_halstead_volume": hal_vol_avg,
                "avg_halstead_difficulty": hal_diff_avg,
                "avg_halstead_effort": hal_effort_avg,
                "avg_halstead_time": hal_time_avg,
                "avg_halstead_bugs": hal_bugs_avg,
                "files_ignored": files_ignored,
                "avg_sloc": avg_sloc,
                "avg_lloc": avg_lloc,
                "avg_comments": avg_comment,
                "avg_blank_lines": avg_blank,
                "maintainability_index": avg_mi
            }
            # Add the CC grade (for example purposes, this is a simple grade)
            cc_grade = "A" if avg_cc < 5 else "B" if avg_cc < 10 else "C"
            repos_df.at[index, 'cc_grade'] = cc_grade
        else:
            na_val = 'N/A'
            # Add placeholders if no data is found
            new_row = {
                "URL": na_val,
                "Repository": na_val,
                "Stars": na_val,
                "Forks": na_val,
                "Search_by": na_val,
                "Search_order": na_val,
                "avg_cc": na_val,
                "total_cc": na_val,
                "Avg_halstead_volume": na_val,
                "avg_halstead_difficulty": na_val,
                "avg_halstead_effort": na_val,
                "avg_halstead_time": na_val,
                "avg_halstead_bugs": na_val,
                "files_ignored": na_val,
                "avg_sloc": na_val,
                "avg_lloc": na_val,
                "avg_comments": na_val,
                "avg_blank_lines": na_val,
                "maintainability_index": na_val
            }
        

        with open("True_Updated_repo_calcs.csv", 'a', newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(new_row.values())

# Usage
csv_file = "MY_CSV.csv"  # Replace with your actual CSV file path
process_repositories(csv_file)






