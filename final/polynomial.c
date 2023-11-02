/*
POLYNOMIAL SUM CALCULATOR
by- Adhikrit Gupta
Haryana, India
*/
#include<stdio.h>
#include<stdlib.h>
typedef struct node
{
    int coeff,power;
    struct node *next;
}NODE;

NODE* create(NODE*);
void display(NODE*);
NODE* insert(NODE*,NODE*);
NODE* add(NODE*, NODE*);
int main()
{
    NODE *head1=NULL, *head2=NULL, *head3=NULL;
    printf("Enter the 1st polynomial in sorted order\n");
    head1=create(head1);
    printf("Enter the second polynomial in sorted order\n");
    head2=create(head2);
    head3=add(head1,head2);
    printf("Sum of the polynomials is:\n");
    display(head3);
    printf("\n");
    return 0;
}

NODE* create(NODE *head)
{
    NODE* temp2=NULL;
    while (1)
    {
        NODE *temp=malloc(sizeof(NODE));
        printf("Enter coefficient term: ");
        scanf("%d", &temp->coeff);
        printf("Enter power: ");
        scanf("%d", &temp->power);
        if(temp2==NULL)
        {
            temp2=temp;
            head=temp2;
        }
        else
        {
            temp2->next=temp;
            temp2=temp2->next;
        }
        if(temp2->power==0)
            break;
    }
    temp2->next=NULL;
    return head;
}

void display(NODE *head)
{
    while (head!=NULL)
    {
        if(head->coeff>0)
            printf("+ ");
        printf("%d",head->coeff);
        if(head->power!=0)
            printf("x^%d ",head->power);
        head=head->next;
    }
}

NODE* add(NODE* head1, NODE* head2)
{
    NODE* head3=NULL;
    while (head1!=NULL&&head2!=NULL)
    {
        NODE* temp=malloc(sizeof(NODE));
        if(head1->power==head2->power)
        {
            temp->coeff=head1->coeff+head2->coeff;
            temp->power=head1->power;
            temp->next=NULL;
            head3=insert(head3,temp);
            head1=head1->next;
            head2=head2->next;
        }
        else if(head1->power>head2->power)
        {
            temp->power=head1->power;
            temp->coeff=head1->coeff;
            temp->next=NULL;
            head3=insert(head3,temp);
            head1=head1->next;
        }
        else
        {
            temp->power=head2->power;
            temp->coeff=head2->coeff;
            temp->next=NULL;
            head3=insert(head3,temp);
            head2=head2->next;
        }
    }
    return head3;
}

NODE* insert(NODE* head3, NODE* temp)
{
    NODE* temp2=head3;
    if(head3==NULL)
    {
        head3=temp;
    }
    else
    {
        while (temp2->next!=NULL)
        {
            temp2=temp2->next;
        }
        temp2->next=temp;
    }
    return head3;
}