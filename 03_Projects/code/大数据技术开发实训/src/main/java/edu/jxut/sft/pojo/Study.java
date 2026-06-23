package edu.jxut.sft.pojo;

/**
 * 课件实体类
 */
public class Study {
    private Integer id;
    private String name;          // 课件资源名
    private String subjectName;   // 所属科目
    private String description;   // 课件简介
    private String detail;        // 课件详情
    private String filePath;      // 课件附件路径
    private String creator;       // 创建人
    private String createTime;    // 创建时间

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getSubjectName() { return subjectName; }
    public void setSubjectName(String subjectName) { this.subjectName = subjectName; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public String getDetail() { return detail; }
    public void setDetail(String detail) { this.detail = detail; }
    public String getFilePath() { return filePath; }
    public void setFilePath(String filePath) { this.filePath = filePath; }
    public String getCreator() { return creator; }
    public void setCreator(String creator) { this.creator = creator; }
    public String getCreateTime() { return createTime; }
    public void setCreateTime(String createTime) { this.createTime = createTime; }
}
